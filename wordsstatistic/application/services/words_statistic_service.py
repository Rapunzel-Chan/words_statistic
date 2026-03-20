import asyncio
import uuid
from typing import Dict, List
from ...domain.entities.words_statistic import WordStatistics, ProcessingResult
from ...domain.interfaces.repos import IWordStatisticsRepository, IFileProcessor


class WordStatisticsService:
    """Сервис для работы со статистикой слов"""

    def __init__(
            self,
            file_processor: IFileProcessor,
            repository: IWordStatisticsRepository
    ):
        self.file_processor = file_processor
        self.repository = repository
        self._tasks: Dict[str, ProcessingResult] = {}
        self._semaphore = asyncio.Semaphore(3)  # Ограничиваем кол-во одновременных обработок

    async def process_file_async(self, file_path: str) -> str:
        """
        Асинхронная обработка файла
        Возвращает ID задачи
        """
        task_id = str(uuid.uuid4())

        # Создаем задачу
        self._tasks[task_id] = ProcessingResult(
            task_id=task_id,
            status="processing"
        )

        # Запускаем обработку в фоне
        asyncio.create_task(self._process_file_task(task_id, file_path))

        return task_id

    async def _process_file_task(self, task_id: str, file_path: str):
        """Фоновая задача обработки файла"""
        try:
            async with self._semaphore:  # Ограничиваем параллельные обработки
                # Получаем статистику
                statistics = await self.file_processor.process_file(file_path)

                # Сохраняем результат
                result_path = await self.repository.save(statistics)

                # Обновляем статус задачи
                self._tasks[task_id] = ProcessingResult(
                    task_id=task_id,
                    status="completed",
                    result_path=result_path
                )
        except Exception as e:
            self._tasks[task_id] = ProcessingResult(
                task_id=task_id,
                status="failed",
                error=str(e)
            )

    async def get_task_status(self, task_id: str) -> ProcessingResult:
        """Получает статус задачи"""
        return self._tasks.get(task_id)
