import logging


import os
import sys
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)
from Error.dataclass.ValidationError import ValidationError

class JsonValidator:
    def __init__(self):
        """"

        Imposta il logger per gli avvisi delle eccezioni,
        crea una schema del json, dove in:
        1) required_fields la chiave rappresenta il field
        e il valore il tipo del valore che ci aspetta.
        2) value_ranges la chiave è il field e il valore il range del valore che ci aspetta
        nel json
        
        User Schema: Da definire

        """

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        self.song_schema ={
            'required_fields': {
                'id': str,
                'artist_name': str,
                'genre': str,
                'name': str,
                'duration_ms': int,
                'explicit': bool,
                'release_date': str,
                'popularity': int,
                'danceability': float,
                'acousticness': float,
                'energy': float,
                'speechiness': float,
                'valence': float,
                'time_signature': int,
                'mode': int,
                'loudness': float,
                'key': int
            },
            'value_ranges': {
                'popularity': (0, 100),
                'danceability': (0.0, 1.0),
                'acousticness': (0.0, 1.0),
                'energy': (0.0, 1.0),
                'speechiness': (0.0, 1.0),
                'valence': (0.0, 1.0),
                'loudness': (-60.0, 0.0),
                'key': (0, 11),
                'mode': (0, 1),
                'time_signature': (3, 7)
            }
        }

        self.user_schema = {
            'required_fields':{
                'id': str,
                'history' : list
            }
        }

    def setting_error(self, field, error_type, message, value, expected):
        """

        Struttura l'errore in 5 valori diversi:
        field -> il field su cui "corre" l'errore
        erro type -> il tipo di errore
        message -> il messaggio
        value -> il valore
        expected -> il valore o il type del field che ci si aspetta

        """

        return ValidationError(
            field=field,
            error_type=error_type,
            message=message,
            value=value,
            expected=expected
        )
    
    def validate_values_song(self, song_data):

        """

        Valida se il range dei valori nel json song_data rientrano 
        nello schema value_ranges impostato nel costruttore.

        Ogni voltra che viene identificato un errore l'errore 
        viene salvato seguento la struttura di ValidationError.

        """

        errors = []

        for field, (min_val, max_val) in self.song_schema['value_ranges'].items():
            try:
                value = song_data[field]

                if value is None:

                    errors.append(self.setting_error(
                        field, 'null_values', f'Valore nullo non permesso per {field}', value, f'valore tra {min_val} e {max_val}'))

                if not min_val <= value <= max_val:

                    errors.append(self.setting_error(
                        field, 'out_of_range', f'valore fuori range per {field}', value, f'valore tra {min_val} e {max_val}'
                    ))
                    
            except KeyError:
                errors.append(self.setting_error(
                        field, 'missing_field', f'Campo mancante : {field}', None, f'valore tra {min_val} e {max_val}'
                    ))
                
            except Exception as e:
                self.logger.error(f'Errore inaspettate durande la validazione di {field} : {str(e)}')
                errors.append(self.setting_error(
                    field, 'unaxpected_error', f'Errore inaspettato : {str(e)}', None, f'valore tra {min_val} e {max_val}'
                ))

        if errors:
            for error in errors:
                self.logger.warning(
                    f'Errore di validazione valori : {error.field} - {error.message}'
                )
            
            return False, errors

        return True, errors

    def validate_field_type_song(self, song_data):

        """

        Valida se in song_data sono presenti i field in required_fields e verifica 
        se anche il type_field è quello che ci si aspetta da required_fields
        nello schema value_ranges impostato nel costruttore.
        
        Ogni voltra che viene identificato un errore l'errore 
        viene salvato seguento la struttura di ValidationError.

        """

        errors = []

        for field, expected_type in self.song_schema['required_fields'].items():
            try:
                if not field in song_data:
                    errors.append(self.setting_error(
                        field, 'missin_field', f'manca {field} in {song_data}', None, field
                    ))

                value = song_data[field]

                if not isinstance(value, expected_type):
                    errors.append(self.setting_error(
                        field, 'invalid_type', f'Tipo non valido per {field}', type(value), expected_type
                    ))

                if value is None:
                    errors.append(self.setting_error(
                        field, 'null_value', f'Valore nullo non permesso per {field}', value, expected_type
                    ))

            except Exception as e:
                self.logger.error(f'Erore inaspettate durante la vlidazione di {field}: {str(e)}')
                errors.append(self.setting_error(
                    field, 'unexpected_error', f'Errore inaspettate : {str(e)}', None, expected_type
                ))

        if errors:
            for error in error:
                self.logger.warning(
                    f'Errore di validazione valori : {error.field} - {error.message}'
                )
            
            return False, errors

        return True, errors
    
    def validate_song(self, song_data):

        """
        Viene verificato se le validazioni dei field e type_field e dei valori 
        è andato a buon fine

        """

        all_errors = []

        success, errors = self.validate_field_type_song(song_data=song_data)
        if not success:
            all_errors.extend(errors)

        success, errors = self.validate_values_song(song_data=song_data)
        if not success:
            all_errors.extend(errors)

        if all_errors:
            self.logger.error(f'Validazione fallita con {len(all_errors)} errori')
            return False
        
        self.logger.info('Validazione completata con successo')
        return True