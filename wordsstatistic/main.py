from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .api.endpoints import report
from .core.container import Container
from .infrastructure.config.settings import settings


def create_app() -> FastAPI:
    """Фабрика приложения"""

    app = FastAPI(
        title="Word Statistics API",
        description="API for collecting word statistics from text files",
        version="1.0.0"
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # DI контейнер
    container = Container()
    app.container = container

    # Роутеры
    app.include_router(report.router)

    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}

    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        workers=1  # Для разработки
    )
