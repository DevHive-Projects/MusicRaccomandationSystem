import logging
import os
import os
import sys
import traceback
import concurrent

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)
from Error.dataclass.ProcessingResultBatch import ProcessingResults
from Error.dataclass.BatchError import BatchError
from Error.dataclass.BatchErrorCollection import BatchErrorCollection
from interfaces.BatchProcessorInterface import BatchProcessorInterface

from typing import List, Dict
from time import sleep
from multiprocessing import Manager, cpu_count
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BatchProcessor(BatchProcessorInterface):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
            cls.instance._initialize = False
        return cls.instance

    def __init__(self,max_retries, retry_delay, json_manager):
        if not self._initialize:
            self.initialize(max_retries, retry_delay, json_manager)
    
    def initialize(self, max_retries, retry_delay, json_manager):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.json_manager = json_manager

        self.num_workers = cpu_count()
        self.manager = Manager()

        self.completed_batches = self.manager.Value('i', 0)
        self.failed_batches = self.manager.Value('i', 0)

        self.counter_lock = self.manager.Lock()

        self.error_collection = BatchErrorCollection()

        self._initialize = True

    @classmethod
    def get_instance(self, cls):
        return cls.instance

    def create_error (self, e, batch_index, worker_id, attempt, context):
        """
        Metodo per creare oggetti BatchError con contest
        """

        return BatchError(
            error_message = str(e),
            error_type = type(e),
            batch_index = batch_index,
            worker_id = worker_id,
            stack_trace = traceback.format_exc(),
            attempt_number = attempt,
            context = {
                'max_retries' : self.max_retries,
                'retry_delay': self.retry_delay,
                **(context or {})
            }
        )

    def process_batch_with_retry(self, batch_data : List[Dict],):
        
        """"
        Processa i batch con meccanismo di retry
        """

        worker_id = os.getpid()
        batch_index = batch_data['batch_index']
        data = batch_data['data']

        attempt = 1
        last_error = None

        while attempt <= self.max_retries:
            try:
                logger.info(f'Tentativo {attempt} per batch {batch_index}')

                processed_data = self.json_manager.process_batch(data)
                
                if processed_data:

                    with self.counter_lock:
                        self.completed_batches.value += 1

                    return ProcessingResults(
                        success = True,
                        data = processed_data,
                        error_type = None,
                        batch_index = batch_index,
                        attempt = attempt,
                        worker_id = worker_id
                    )
            except Exception as e:
                batch_error = self.create_error(
                    str(e), batch_index, worker_id, attempt, {'batch_size': len(data), 'retry_attempt' : attempt}
                )
                self.error_collection.add_error(batch_error)

                logger.error(
                    f'Errore nel processamento del batch {batch_index}',
                    extra={
                        'error_details' : batch_error.to_dic(),
                        'processor_state' : {
                            'completed_batches' : self.completed_batches.value,
                            'failed_batches' : self.failed_batches.value
                        }
                    }
                )

                if attempt < self.max_retries:
                    sleep(self.retry_delay)

                else:
                    self.failed_batches.value += 1
            attempt += 1
        return ProcessingResults(
            success = False,
            data = [],
            error_type = str(last_error),
            batch_index = batch_index,
            attempt = attempt - 1,
            worker_id = worker_id
        )
    

    def process_all_batch(self, batches, start_from_batch: int):
        #self.batch_errors.set_total_batches(len(batches))
        results = []

        batch_data =[
            {
                'batch_index' : i+start_from_batch,
                'data' : batch,
            }
            for i, batch in enumerate(batches[start_from_batch:])
        ]

        try:
            with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
                future_to_batch = {
                    executor.submit(self.process_batch_with_retry, batch) : batch
                    for batch in batch_data
                }

                for future in concurrent.futures.as_completed(future_to_batch):

                    try:
                        result = future.result()
                        if result.success:
                            logger.info(f'Batch {result.batch_index} processato con successo')
                            results.append(result)
                    except Exception as e:
                        error = self.create_error(e, batch_data['batch_index'], os.getpid(), 1, 
                                                  {'phase' : 'Future processing'})
                        self.error_collection.add_error(error)
                        logging.error(f'Errore di preelaborazione del batch {batch_data["batch_index"]}',
                                      extra = {'errore_details': error.to_dict()})
        except Exception as e:
            error = self.create_error(
                            e, batch_data['batch_index'], os.getpid(), 1,
                            {'phase' : 'parallel processing'}
                        )
            self.error_collection.add_error(error)
            logging.error(f'Errore di elaborazione parallela del batch {batch_data["batch_index"]}',
                            extra = {'errore_details': error.to_dict()})
            
