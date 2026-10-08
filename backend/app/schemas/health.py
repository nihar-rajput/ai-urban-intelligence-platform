from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class GPUInfo(BaseModel):
    is_available: bool = Field(..., description="Whether PyTorch detects CUDA support")
    device_name: Optional[str] = Field(None, description="Name of the GPU device")
    device_count: int = Field(0, description="Number of detected CUDA devices")
    allocated_memory_mb: Optional[float] = Field(None, description="Current CUDA memory allocated in MB")
    reserved_memory_mb: Optional[float] = Field(None, description="Current CUDA memory reserved in MB")


class ModelStatus(BaseModel):
    name: str
    loaded: bool
    path: str
    device: str
    supported_classes: list[str] = []


class HealthResponse(BaseModel):
    status: str = "ok"
    project: str
    version: str
    timestamp: str
    gpu: GPUInfo
    active_streams: int
    models: Dict[str, ModelStatus]
