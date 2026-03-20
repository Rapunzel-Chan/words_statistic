import asyncio
import uuid
from typing import Dict, Optional

from ...domain.entities.words_statistic import ProcessingResult, WordStatistics
from ...domain.interfaces.repos import IFileProcessor, IWordStatisticsRepository


class WordStatisticsService:
    """Сервис для работы со статистикой слов"""

    def __init__(self, file_processor: IFileProcessor, repository: IWordStatisticsRepository, max_concurrent: int = 3):
        self.file_processor = file_processor
        self.repository = repository
        self._tasks: Dict[str, ProcessingResult] = {}
        self._semaphore = asyncio.Semaphore(max_concurrent)

    async def process_file_async(self, file_path: str, repository=None) -> str:
        """
        Асинхронная обработка файла
        Возвращает ID задачи
        """
        task_id = str(uuid.uuid4())

        # Создаем задачу
        self._tasks[task_id] = ProcessingResult(task_id=task_id, status="processing")

        # Запускаем обработку в фоне
        asyncio.create_task(self._process_file_task(task_id, file_path, repository))

        print(f"Task {task_id}: Created for file {file_path}")
        return task_id

    async def _process_file_task(self, task_id: str, file_path: str, repository=None):
        """Фоновая задача обработки файла"""
        try:
            async with self._semaphore:
                print(f"Task {task_id}: Starting processing (active tasks: {self._semaphore._value})")

                # Проверяем существование файла перед обработкой
                import os

                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"File not found: {file_path}")

                # Получаем статистику
                statistics = await self.file_processor.process_file(file_path)

                # Сохраняем результат
                result_path = await self.repository.save(statistics)

                # Обновляем статус задачи
                self._tasks[task_id] = ProcessingResult(task_id=task_id, status="completed", result_path=result_path)
                print(f"Task {task_id}: Completed successfully")

        except Exception as e:
            print(f"Task {task_id}: Failed with error: {str(e)}")
            self._tasks[task_id] = ProcessingResult(task_id=task_id, status="failed", error=str(e))
        finally:
            # Очищаем временный файл после обработки (даже если была ошибка)
            if repository and file_path:
                try:
                    await repository.cleanup(file_path)
                    print(f"Task {task_id}: Cleaned up {file_path}")
                except Exception as e:
                    print(f"Task {task_id}: Error during cleanup: {e}")

    async def get_task_status(self, task_id: str) -> Optional[ProcessingResult]:
        """Получает статус задачи"""
        return self._tasks.get(task_id)
