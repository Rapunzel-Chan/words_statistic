from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from typing import Optional
import os

from ...application.dto.requests import ReportExportResponse
from ...application.services.words_statistic_service import WordStatisticsService
from ...infrastructure.repos.file_repo import FileRepository
from ...infrastructure.config.settings import settings

router = APIRouter(prefix="/public/report", tags=["report"])


@router.post("/export", response_model=ReportExportResponse)
async def export_report(
        background_tasks: BackgroundTasks,
        file: UploadFile = File(...),
        word_service: WordStatisticsService = None  # Будет внедрено через dependency
):
    """
    Экспорт отчета со статистикой слов из текстового файла
    """
    try:
        # Проверяем размер файла
        file_size = 0
        content = await file.read()
        file_size = len(content)

        if file_size > settings.max_file_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Max size: {settings.max_file_size} bytes"
            )

        # Сохраняем файл
        repository = FileRepository()
        file_path = await repository.save_uploaded_file(content, file.filename)

        # Запускаем обработку
        task_id = await word_service.process_file_async(file_path)

        # Добавляем задачу на очистку
        background_tasks.add_task(repository.cleanup, file_path)

        return ReportExportResponse(
            task_id=task_id,
            status="processing",
            message="File is being processed. Use task_id to check status."
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/status/{task_id}")
async def get_export_status(
        task_id: str,
        word_service: WordStatisticsService = None
):
    """
    Проверка статуса обработки файла
    """
    result = await word_service.get_task_status(task_id)

    if not result:
        raise HTTPException(status_code=404, detail="Task not found")

    if result.status == "completed":
        return {
            "task_id": result.task_id,
            "status": result.status,
            "download_url": f"/public/report/download/{result.result_path}"
        }
    elif result.status == "failed":
        return {
            "task_id": result.task_id,
            "status": result.status,
            "error": result.error
        }
    else:
        return {
            "task_id": result.task_id,
            "status": result.status
        }


@router.get("/download/{filename:path}")
async def download_report(filename: str):
    """
    Скачивание готового отчета
    """
    file_path = os.path.join(settings.reports_dir, os.path.basename(filename))

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        file_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=os.path.basename(filename)
    )
