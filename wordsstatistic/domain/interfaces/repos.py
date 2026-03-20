from abc import ABC, abstractmethod
from typing import List
from ..entities.words_statistic import WordStatistics


class IWordStatisticsRepository(ABC):
    """Интерфейс репозитория статистики слов"""

    @abstractmethod
    async def save(self, statistics: List[WordStatistics]) -> str:
        """Сохраняет статистику и возвращает путь к файлу"""
        pass


class IFileProcessor(ABC):
    """Интерфейс процессора файлов"""

    @abstractmethod
    async def process_file(self, file_path: str) -> List[WordStatistics]:
        """Обрабатывает файл и возвращает статистику"""
        pass
