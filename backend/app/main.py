import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.db.session import init_db
from backend.app.api.v1.router import api_v1_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}...")
    os.makedirs(settings.STORAGE_DIR, exist_ok=True)
    os.makedirs(settings.SAMPLE_VIDEOS_DIR, exist_ok=True)
    os.makedirs(settings.MODELS_DIR, exist_ok=True)
    os.makedirs(settings.DATASETS_DIR, exist_ok=True)

    await init_db()
    logger.info("Application startup complete. Ready for video ingestion & telemetry.")
    yield
    # Shutdown
    logger.info("Shutting down AI Urban Intelligence Platform...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Simulated Bus-Mounted Camera Edge AI & Urban Road Defect Intelligence System (SIH Problem Statement SIH26124)",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount evidence directory for serving incident snapshots
os.makedirs(settings.STORAGE_DIR, exist_ok=True)
app.mount("/evidence", StaticFiles(directory=settings.STORAGE_DIR), name="evidence")

# Include API v1 Router
app.include_router(api_v1_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "docs_url": "/docs",
        "api_v1": settings.API_V1_STR
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
