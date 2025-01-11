from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional

@dataclass
class BatchError:
    """
    Rappresenta un singolo errore di processamento di un batc
    """
    error_message : str
    error_type : str
    batch_index : int
    worker_id : int
    timestamp : field(default_factory = datetime.now)
    stack_trace : Optional[str] = None
    attempt : int = 1
    context : Dict = field(default_factory = dict)

    def to_dic(self) -> Dict:
        """
        Converte l'errore in un dizionario
        """

        return {
            'error_message' : self.error_message,
            'error_type' : self.error_type,
            'batch_index' : self.batch_index,
            'worker_id' : self.worker_id,
            'timestamp' : self.timestamp,
            'stack_trace' : self.stack_trace,
            'attempt' : self.attempt,
            'context' : self.context
        }
    
    def get_error_indetifier(self) -> str:
        """
        Restituisce un identificativo univoco per l'errore
        """

        return f'{self.batch_index}_{self.attempt}_{self.error_type}'
    
    