from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class VehicleCountResponse(BaseModel):
    camera_id: str
    counts_by_class: Dict[str, int]
    total_vehicles: int
    density_level: str  # LOW, MEDIUM, HIGH, CONGESTED
    calculated_at: datetime


class AnalyticsOverview(BaseModel):
    total_incidents: int
    pending_reviews: int
    resolved_incidents: int
    incidents_by_type: Dict[str, int]
    incidents_by_severity: Dict[str, int]
    traffic_density_by_bus: Dict[str, str]
    total_vehicles_tracked: int
