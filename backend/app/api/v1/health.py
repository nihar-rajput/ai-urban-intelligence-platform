from datetime import datetime, timezone
import os
import torch
from fastapi import APIRouter
from backend.app.core.config import settings
from backend.app.schemas.health import HealthResponse, GPUInfo, ModelStatus

router = APIRouter(tags=["Health & Diagnostics"])


@router.get("/health", response_model=HealthResponse)
async def get_health():
    # GPU Diagnostics
    cuda_available = torch.cuda.is_available()
    device_name = torch.cuda.get_device_name(0) if cuda_available else None
    device_count = torch.cuda.device_count() if cuda_available else 0

    alloc_mem = None
    res_mem = None
    if cuda_available:
        try:
            alloc_mem = round(torch.cuda.memory_allocated(0) / (1024 * 1024), 2)
            res_mem = round(torch.cuda.memory_reserved(0) / (1024 * 1024), 2)
        except Exception:
            pass

    gpu_info = GPUInfo(
        is_available=cuda_available,
        device_name=device_name,
        device_count=device_count,
        allocated_memory_mb=alloc_mem,
        reserved_memory_mb=res_mem
    )

    # Models Status
    vehicle_model_exists = os.path.exists(settings.YOLO_VEHICLE_MODEL)
    defect_model_exists = os.path.exists(settings.YOLO_ROAD_DEFECT_MODEL)

    models_info = {
        "vehicle_detector": ModelStatus(
            name="YOLO Vehicle & Road Object Detector",
            loaded=vehicle_model_exists,
            path=settings.YOLO_VEHICLE_MODEL,
            device=settings.DEVICE,
            supported_classes=["car", "bus", "truck", "motorcycle", "bicycle", "person"]
        ),
        "road_defect_detector": ModelStatus(
            name="Road Defect & Hazard Detector",
            loaded=defect_model_exists,
            path=settings.YOLO_ROAD_DEFECT_MODEL,
            device=settings.DEVICE,
            supported_classes=["pothole", "longitudinal_crack", "alligator_crack", "waterlogging"] if defect_model_exists else []
        )
    }

    return HealthResponse(
        status="ok",
        project=settings.PROJECT_NAME,
        version=settings.VERSION,
        timestamp=datetime.now(timezone.utc).isoformat(),
        gpu=gpu_info,
        active_streams=0,
        models=models_info
    )
