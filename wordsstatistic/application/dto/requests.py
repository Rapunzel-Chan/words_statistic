from pydantic import BaseModel


class ReportExportRequest(BaseModel):
    """DTO для запроса экспорта отчета"""

    filename: str
    file_size: int


class ReportExportResponse(BaseModel):
    """DTO для ответа на запрос экспорта"""

    task_id: str
    status: str
    message: str
