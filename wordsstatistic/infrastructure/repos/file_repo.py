import os
import shutil
from typing import List
from datetime import datetime
from ...domain.entities.words_statistic import WordStatistics
from ...domain.interfaces.repos import IWordStatisticsRepository
from ..services.excel_generator import ExcelGenerator


class FileRepository(IWordStatisticsRepository):
    """Репозиторий для сохранения статистики в файл"""

    def __init__(self, upload_dir: str = "uploads", reports_dir: str = "reports"):
        self.upload_dir = upload_dir
        self.reports_dir = reports_dir
        os.makedirs(upload_dir, exist_ok=True)
        os.makedirs(reports_dir, exist_ok=True)
        self.excel_generator = ExcelGenerator(reports_dir)

    async def save_uploaded_file(self, file_content: bytes, filename: str) -> str:
        """Сохраняет загруженный файл"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{filename}"
        file_path = os.path.join(self.upload_dir, safe_filename)

        with open(file_path, "wb") as f:
            f.write(file_content)

        return file_path

    async def save(self, statistics: List[WordStatistics]) -> str:
        """Сохраняет статистику в Excel файл"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"word_statistics_{timestamp}.xlsx"

        output_path = await self.excel_generator.generate(statistics, filename)
        return output_path

    async def cleanup(self, file_path: str):
        """Удаляет временные файлы"""
        if os.path.exists(file_path):
            os.remove(file_path)
