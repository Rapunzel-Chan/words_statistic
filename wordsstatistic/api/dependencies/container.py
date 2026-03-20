from fastapi import Request
from ...application.services.words_statistic_service import WordStatisticsService
from ...infrastructure.services.txt_processor import WordProcessor
from ...infrastructure.repos.file_repo import FileRepository
from ...infrastructure.config.settings import settings

# Глобальный экземпляр сервиса (синглтон)
_word_service = None


async def get_word_statistics_service(request: Request = None) -> WordStatisticsService:
    """Dependency для получения сервиса статистики слов"""
    global _word_service

    if _word_service is None:
        processor = WordProcessor(chunk_size=settings.chunk_size)
        repository = FileRepository(
            upload_dir=settings.upload_dir,
            reports_dir=settings.reports_dir
        )
        _word_service = WordStatisticsService(
            file_processor=processor,
            repository=repository,
            max_concurrent=settings.max_concurrent_tasks
        )

    return _word_service
