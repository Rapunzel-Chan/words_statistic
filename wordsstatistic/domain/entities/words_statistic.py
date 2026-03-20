from dataclasses import dataclass
from typing import Dict, List


@dataclass
class WordStatistics:
    """Сущность статистики слов"""
    word_form: str
    total_count: int
    line_counts: List[int]

    def to_dict(self) -> Dict:
        return {
            "word_form": self.word_form,
            "total_count": self.total_count,
            "line_counts": self.line_counts
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'WordStatistics':
        return cls(
            word_form=data["word_form"],
            total_count=data["total_count"],
            line_counts=data["line_counts"]
        )


@dataclass
class ProcessingResult:
    """Результат обработки файла"""
    task_id: str
    status: str
    result_path: str = None
    error: str = None
