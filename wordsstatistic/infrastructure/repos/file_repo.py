import asyncio
import os
from datetime import datetime
from typing import List

from ...domain.entities.words_statistic import WordStatistics
from ...domain.interfaces.repos import IWordStatisticsRepository
from ..services.excel_generator import ExcelGenerator


class FileRepository(IWordStatisticsRepository):
    """Репозиторий для сохранения статистики в файл"""

    def __init__(self, upload_dir: str = "uploads", reports_dir: str = "reports"):
        current_file = os.path.abspath(__file__)
        self.project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file))))

        self.upload_dir = os.path.join(self.project_root, upload_dir)
        self.reports_dir = os.path.join(self.project_root, reports_dir)

        # Создаем директории
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.reports_dir, exist_ok=True)

        self.excel_generator = ExcelGenerator(self.reports_dir)

        print(f"Project root: {self.project_root}")
        print(f"Upload directory: {self.upload_dir}")
        print(f"Reports directory: {self.reports_dir}")

    async def save_uploaded_file(self, file_content: bytes, filename: str) -> str:
        """Сохраняет загруженный файл"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{filename}"
        file_path = os.path.join(self.upload_dir, safe_filename)

        # Сохраняем файл
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._save_file, file_path, file_content)

        print(f"File saved: {file_path}")
        return file_path

    def _save_file(self, file_path: str, content: bytes):
        """Синхронное сохранение файла"""
        with open(file_path, "wb") as f:
            f.write(content)

    async def save(self, statistics: List[WordStatistics]) -> str:
        """Сохраняет статистику в Excel файл"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"word_statistics_{timestamp}.xlsx"

        output_path = await self.excel_generator.generate(statistics, filename)
        return output_path

    async def cleanup(self, file_path: str):
        """Удаляет временные файлы"""
        try:
            if os.path.exists(file_path):
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, os.remove, file_path)
                print(f"Cleaned up: {file_path}")
        except Exception as e:
            print(f"Error cleaning up {file_path}: {e}")
