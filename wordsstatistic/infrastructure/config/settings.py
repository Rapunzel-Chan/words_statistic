from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения из .env файла"""

    # Основные настройки
    app_name: str = "Word Statistics API"
    app_version: str = "1.0.0"
    debug: bool = False

    # Ограничения
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    max_concurrent_tasks: int = 3
    chunk_size: int = 1024 * 1024  # 1MB

    # Директории
    upload_dir: str = "uploads"
    reports_dir: str = "reports"

    # Логирование
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)


settings = Settings()
