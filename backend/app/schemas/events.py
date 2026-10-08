from datetime import datetime
from typing import Optional, Any, Dict
from pydantic import BaseModel, Field


class IncidentEventBase(BaseModel):
    event_type: str = Field(..., description="e.g. POTHOLE, CRACK, PROXIMITY_CONFLICT, RASH_DRIVING_CANDIDATE")
    severity: str = Field("MEDIUM", description="LOW, MEDIUM, HIGH, CRITICAL")
    confidence: float = Field(..., ge=0.0, le=1.0)
    camera_id: str = Field(..., description="Camera ID e.g. BUS-001")
    track_id: Optional[int] = None
    timestamp: float = Field(..., description="Stream relative timestamp in seconds")
    latitude: float
    longitude: float
    is_simulated_gps: bool = True
    evidence_image_path: Optional[str] = None
    review_status: str = Field("PENDING", description="PENDING, VERIFIED, FALSE_POSITIVE, RESOLVED")
    review_notes: Optional[str] = None
    metadata_json: Optional[str] = None


class IncidentEventCreate(IncidentEventBase):
    event_uuid: Optional[str] = None


class IncidentReviewUpdate(BaseModel):
    review_status: str = Field(..., description="VERIFIED, FALSE_POSITIVE, RESOLVED, PENDING")
    review_notes: Optional[str] = None


class IncidentEventRead(IncidentEventBase):
    id: int
    event_uuid: str
    created_at: datetime

    class Config:
        from_attributes = True


class IncidentFilterParams(BaseModel):
    camera_id: Optional[str] = None
    event_type: Optional[str] = None
    severity: Optional[str] = None
    review_status: Optional[str] = None
    limit: int = 50
    offset: int = 0
