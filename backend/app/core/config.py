import os
from typing import List
import torch
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    PROJECT_NAME: str = "AI Urban Intelligence Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DEBUG: bool = True

    # CORS configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./urban_intelligence.db"

    # Inference & Hardware Acceleration
    DEVICE: str = "cuda" if torch.cuda.is_available() else "cpu"
    DETECTION_CONF_THRESHOLD: float = 0.35
    IOU_THRESHOLD: float = 0.45
    MAX_DETECTION_BATCH_SIZE: int = 4

    # Storage paths (relative to workspace root)
    STORAGE_DIR: str = "evidence"
    SAMPLE_VIDEOS_DIR: str = "sample_videos"
    DATASETS_DIR: str = "datasets"
    MODELS_DIR: str = "models"
    MAX_UPLOAD_SIZE_MB: int = 500
    ALLOWED_EXTENSIONS: List[str] = ["mp4", "avi", "mov", "mkv", "webm"]

    # Fleet simulation defaults
    DEFAULT_FLEET_IDS: List[str] = ["BUS-001", "BUS-002", "BUS-003"]
    ENABLE_DEMO_TELEMETRY: bool = True
    DEMO_TELEMETRY_LAT: float = 28.6139  # New Delhi reference
    DEMO_TELEMETRY_LON: float = 77.2090

    # Model paths
    YOLO_VEHICLE_MODEL: str = "models/yolov8n.pt"
    YOLO_ROAD_DEFECT_MODEL: str = "models/road_defects_best.pt"


settings = Settings()
