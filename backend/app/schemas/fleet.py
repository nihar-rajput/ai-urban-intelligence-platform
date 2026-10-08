from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class CameraSourceBase(BaseModel):
    bus_id: str = Field(..., description="Unique fleet identifier e.g. BUS-001")
    name: str = Field(..., description="Human-readable camera name e.g. Central Delhi Bus Route #412")
    stream_url_or_path: Optional[str] = None
    fps: float = 0.0
    current_lat: Optional[float] = None
    current_lon: Optional[float] = None


class CameraSourceCreate(CameraSourceBase):
    pass


class CameraSourceRead(CameraSourceBase):
    id: int
    status: str
    is_active: bool
    total_frames_processed: int
    total_incidents_detected: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StreamControlCommand(BaseModel):
    action: str = Field(..., description="START, PAUSE, RESUME, STOP, REPLAY")
    playback_speed: Optional[float] = Field(1.0, ge=0.25, le=4.0)
    video_path: Optional[str] = None


class FleetStatusSummary(BaseModel):
    total_buses: int
    active_buses: int
    stopped_buses: int
    sources: List[CameraSourceRead]
