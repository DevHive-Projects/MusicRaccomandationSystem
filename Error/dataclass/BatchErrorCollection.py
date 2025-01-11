from dataclasses import dataclass, field
from typing import Dict, Optional, List
from datetime import datetime

from .BatchError import BatchError

import json

@dataclass
class BatchErrorCollection:
    total_batches : int = 0
    error : List[BatchError] = field(default_factory = list)
    erorrs_counts : Dict[str, int] = field(default_factory = dict) 
    start_time: datetime = field(default_factory=datetime.now) 

    def add_error(self, error : BatchError) -> None:
        """
        Aggiunge un nuovo errore alla collezione
        """
        self.error.append(error)
        self.erorrs_counts[error.error_type] = self.erorrs_counts.get(error.error_type, 0) + 1

    def get_error_summary(self) -> Dict:
        """
        Genera un riepilogo degli errori per il logging
        """

        return {
            'total_batches': self.total_batches,
            'total_errors': len(self.error), 
            'error_distribution': self.erorrs_counts, 
            'error_rate': len(self.error) / self.total_batches if self.total_batches > 0 else 0, 
            'errors_by_batch': {error.batch_index: error.to_dict() for error in self.error}, 
            'processing_duration': (datetime.now() - self.start_time).total_seconds(),
        }

    def get_errors_by_type(self, error_type: str) -> List[BatchError]:
        """Recupera tutti gli errori di un determinato tipo"""
        return [error for error in self.error if error.error_type == error_type]

    def get_errors_for_batch(self, batch_index: int) -> List[BatchError]:
        """Recupera tutti gli errori associati a un determinato batch"""
        return [error for error in self.error if error.batch_index == batch_index]

    def to_json(self, file_path: str) -> None:
        """Salva la collezione di errori in un file JSON"""
        with open(file_path, 'w') as f:
            json.dump({
                'total_batches': self.total_batches,
                'total_errors': len(self.error),
                'processing_duration': (datetime.now() - self.start_time).total_seconds(),
                'errors': [error.to_dict() for error in self.error],
                'error_counts': self.erorrs_counts,
            }, f, indent=2)

    def update_error_counts(self) -> None:
        """Aggiorna i conteggi degli errori"""
        self.erorrs_counts = {} 
        for error in self.error:
            self.erorrs_counts[error.error_type] = self.erorrs_counts.get(error.error_type, 0)