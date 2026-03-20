from fastapi import Request
from ...application.services.words_statistic_service import WordStatisticsService
from ...infrastructure.services.txt_processor import WordProcessor
from ...infrastructure.repos.file_repo import FileRepository
from ...infrastructure.config.settings import settings


async def get_word_statistics_service(request: Request = None) -> WordStatisticsService:
    """Dependency для получения сервиса статистики слов"""
    # В реальном проекте здесь может быть DI контейнер
    processor = WordProcessor(chunk_size=settings.chunk_size)
    repository = FileRepository()
    return WordStatisticsService(processor, repository)
