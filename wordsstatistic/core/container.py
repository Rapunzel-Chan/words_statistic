from dependency_injector import containers, providers

from ..application.services.words_statistic_service import WordStatisticsService
from ..infrastructure.config.settings import settings
from ..infrastructure.repos.file_repo import FileRepository
from ..infrastructure.services.txt_processor import WordProcessor


class Container(containers.DeclarativeContainer):
    """DI контейнер"""

    wiring_config = containers.WiringConfiguration(modules=["..api.endpoints.report"])

    config = providers.Configuration()
    config.from_dict(settings.dict())

    # Репозитории
    file_repository = providers.Singleton(FileRepository, upload_dir=config.upload_dir, reports_dir=config.reports_dir)

    # Сервисы
    word_processor = providers.Singleton(WordProcessor, chunk_size=config.chunk_size)

    word_statistics_service = providers.Singleton(
        WordStatisticsService, file_processor=word_processor, repository=file_repository
    )
