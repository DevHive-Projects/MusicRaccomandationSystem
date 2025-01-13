import pandas as pd
import numpy as np
import logging
import os
import sys
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_dir)
from interfaces.JsonManagerInterface import JsonManagerInterface

from Batch.BatchProcessor import BatchProcessor
from DataManager.Json.JsonValidator import JsonValidator

from abc import abstractmethod
from typing import List, Dict, Optional


class JsonManager(JsonManagerInterface):
    instance = None

    def __new__(cls, *args, **kwargs):

        if cls.instance is None:
            cls.instance = super().__new__(cls)
            cls.instance._initialize = False
        return cls.instance

    def __init__(self, batch_size):
        if not self._initialize:
            self.initialize(batch_size)
        
    def initialize(self, batch_size):
        self.json_validator = JsonValidator()
        self.batch_size = batch_size
        self.dataframe : Optional[pd.DateFrame] = None
        self.batch_processor = BatchProcessor(2,5)

        self._initialize = True 

    @classmethod
    def get_instance(cls):
        return cls.instance

    def process_song_data(self, songs_data : List[Dict]) -> None:
        
        """
        Processa tutti i dati delle canzni utilizzando BatchProcessor
        che sfrutta l'esecuzione di Batch paralleli
        """
        try:
            batches = [songs_data[i:i+self.batch_size]
                    for i in range(0, len(songs_data), self.batch_size)]
            logger.info(f'Avvio processamente di {len(batches)} batch')
            
            results = self.batch_processor.process_all_batch(
                batches = batches,
                start_from_batch = 0,
                json_manager = self.get_instance()
            )

            all_processed_songs = []
            for result in results:
                if result.success:
                    all_processed_songs.extend(result.data)

            if all_processed_songs:
                self.dataframe = pd.DataFrame(all_processed_songs)
                logging.info(f'Dataframe creato con {len(all_processed_songs)} canzoni')
            else:
                logger.warning(f'Nessuna canzone processata con successo')
        except Exception as e:
            logger.error(f'Errore nel processo dei dati : {str(e)}')

    def process_batch(self, batch_data):
        """"
        Processa un singolo batch di canzoni, questa è
        la funzione che viene passata al BatchProcessor
        """

        processed_songs = []
        batch_songs = batch_data

        for song in batch_songs:
            try:
                processed_song = self.process_single_song(song)
                if processed_song:
                    processed_songs.append(processed_song)
                elif processed_song is not None:
                    logger.warning(f'prodess_single_song restituisce un tipo inatteso : {type(processed_song)}')
            except Exception as e:
                logger.error(f'Errore nel processamente della canzone {str(e)}')
        
        return processed_songs

    def process_single_song(self, song : List[Dict]):
        """
        Processa una singola canzone, convertendo da JSON a formato tabellare.
        """

        song_validate_status = self.json_validator.validate_song(song)

        if song_validate_status == True:

            return{
                'son_id' : song['id'],
                'artis_name' : song['artist_name'],
                'genre' : song['genre'],
                'name' : song['name'],
                'duration_ms' : song['duration_ms'],
                'explicit' : 1 if song['explicit'] == True else 0,
                'release_date' : song['release_date'],
                'popularity' : song['popularity'],
                'danceability' : song['danceability'],
                'acousticness' : song['acousticness'],
                'energy' : song['energy'],
                'speechiness' : song['speechiness'],
                'valence' : song['valence'],
                'time_signature' : song['time_signature'],
                'mode' : song['mode'],
                'loudness' : song['loudness'],
                'key' : song['key'],
            }

    def process_user_preferences(self, user_json):
        """"
        Processa lo storico degli ascolti di un utente e crea un profilo
        e crea un profilo dell'utente
        
        """ 

        user_history = {
            'user_id' : user_json['id'],
            'listening_song' : [self.process_song_data(song) for song in user_json['history']]
        }
    
        return user_history
    
    def get_dataset(self):
        return self.dataframe