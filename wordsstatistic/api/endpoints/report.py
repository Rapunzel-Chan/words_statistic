from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Depends
from fastapi.responses import FileResponse
import os

from ...application.dto.requests import ReportExportResponse
from ...application.services.words_statistic_service import WordStatisticsService
from ...infrastructure.repos.file_repo import FileRepository
from ...infrastructure.config.settings import settings
from ..dependencies.container import get_word_statistics_service

router = APIRouter(prefix="/public/report", tags=["report"])


@router.post("/export", response_model=ReportExportResponse)
async def export_report(
        file: UploadFile = File(...),
        word_service: WordStatisticsService = Depends(get_word_statistics_service)
):
    """
    Экспорт отчета со статистикой слов из текстового файла
    """
    try:
        # Проверяем расширение файла
        if not file.filename.endswith('.txt'):
            raise HTTPException(
                status_code=400,
                detail="Only .txt files are supported"
            )

        # Читаем содержимое файла
        content = await file.read()
        file_size = len(content)

        # Проверяем размер
        if file_size > settings.max_file_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Max size: {settings.max_file_size / 1024 / 1024:.0f}MB"
            )

        # Сохраняем файл
        repository = FileRepository(
            upload_dir=settings.upload_dir,
            reports_dir=settings.reports_dir
        )
        file_path = await repository.save_uploaded_file(content, file.filename)

        # Запускаем обработку (очистка будет выполнена внутри сервиса)
        task_id = await word_service.process_file_async(file_path, repository)

        return ReportExportResponse(
            task_id=task_id,
            status="processing",
            message="File is being processed. Use task_id to check status."
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in export_report: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/status/{task_id}")
async def get_export_status(
        task_id: str,
        word_service: WordStatisticsService = Depends(get_word_statistics_service)
):
    """
    Проверка статуса обработки файла
    """
    result = await word_service.get_task_status(task_id)

    if not result:
        raise HTTPException(status_code=404, detail="Task not found")

    if result.status == "completed":
        filename = os.path.basename(result.result_path)
        return {
            "task_id": result.task_id,
            "status": result.status,
            "download_url": f"/public/report/download/{filename}"
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
    safe_filename = os.path.basename(filename)
    file_path = os.path.join(settings.reports_dir, safe_filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        file_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=safe_filename
    )
