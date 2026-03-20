import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.endpoints import report
from .infrastructure.config.settings import settings


def create_app() -> FastAPI:
    """Фабрика приложения"""

    app = FastAPI(
        title=settings.app_name,
        description="API for collecting word statistics from text files",
        version=settings.app_version,
        debug=settings.debug,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Роутеры
    app.include_router(report.router)

    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "app": settings.app_name, "version": settings.app_version}

    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run("wordsstatistic.main:app", host="0.0.0.0", port=8000, reload=settings.debug, workers=1)
