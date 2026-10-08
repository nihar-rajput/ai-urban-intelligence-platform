from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from backend.app.db.session import get_db
from backend.app.models.db_models import IncidentEvent, CameraSource, VehicleCountRecord
from backend.app.schemas.analytics import AnalyticsOverview

router = APIRouter(prefix="/analytics", tags=["Analytics & Traffic"])


@router.get("/overview", response_model=AnalyticsOverview)
async def get_analytics_overview(db: AsyncSession = Depends(get_db)):
    """Compute aggregate analytics for dashboard summary cards."""
    # Count incidents by type
    type_query = select(IncidentEvent.event_type, func.count(IncidentEvent.id)).group_by(IncidentEvent.event_type)
    type_res = await db.execute(type_query)
    by_type = {row[0]: row[1] for row in type_res.all()}

    # Count incidents by severity
    sev_query = select(IncidentEvent.severity, func.count(IncidentEvent.id)).group_by(IncidentEvent.severity)
    sev_res = await db.execute(sev_query)
    by_sev = {row[0]: row[1] for row in sev_res.all()}

    # Total and review statuses
    total_incidents = sum(by_type.values())
    pending_query = select(func.count(IncidentEvent.id)).where(IncidentEvent.review_status == "PENDING")
    pending_res = await db.execute(pending_query)
    pending_count = pending_res.scalar() or 0

    resolved_query = select(func.count(IncidentEvent.id)).where(IncidentEvent.review_status == "RESOLVED")
    resolved_res = await db.execute(resolved_query)
    resolved_count = resolved_res.scalar() or 0

    # Total vehicles tracked across records
    total_vehicles_query = select(func.sum(VehicleCountRecord.count))
    veh_res = await db.execute(total_vehicles_query)
    total_vehicles = veh_res.scalar() or 0
    from backend.app.services.tracking_service import fleet_tracker
    density_map = {
        bus_id: fleet_tracker.get_tracker(bus_id).get_traffic_density()
        for bus_id in ["BUS-001", "BUS-002", "BUS-003"]
    }

    # Sum tracker counted vehicles if DB records are not yet committed
    live_tracker_vehicles = sum(
        len(fleet_tracker.get_tracker(b).counted_track_ids)
        for b in ["BUS-001", "BUS-002", "BUS-003"]
    )
    total_vehicles = max(total_vehicles, live_tracker_vehicles)

    return AnalyticsOverview(
        total_incidents=total_incidents,
        pending_reviews=pending_count,
        resolved_incidents=resolved_count,
        incidents_by_type=by_type,
        incidents_by_severity=by_sev,
        traffic_density_by_bus=density_map,
        total_vehicles_tracked=total_vehicles
    )


@router.get("/vehicles/{camera_id}")
async def get_camera_vehicle_analytics(camera_id: str):
    """Retrieve live unique vehicle counts by category and traffic density for a specific camera."""
    from backend.app.services.tracking_service import fleet_tracker
    tracker = fleet_tracker.get_tracker(camera_id)
    return tracker.get_stats()


@router.get("/anpr")
async def get_anpr_readings(
    camera_id: str = None,
    verification_status: str = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve recent ANPR license plate detections with review status."""
    from backend.app.models.db_models import ANPRReading
    query = select(ANPRReading).order_by(ANPRReading.id.desc()).limit(limit)
    if camera_id:
        query = query.where(ANPRReading.camera_id == camera_id)
    if verification_status:
        query = query.where(ANPRReading.verification_status == verification_status)
    res = await db.execute(query)
    readings = res.scalars().all()
    return [
        {
            "id": r.id,
            "camera_id": r.camera_id,
            "track_id": r.track_id,
            "plate_text": r.plate_text,
            "confidence": r.confidence,
            "evidence_crop_path": r.evidence_crop_path,
            "verification_status": r.verification_status,
            "timestamp": r.timestamp,
            "created_at": r.created_at.isoformat() if r.created_at else None
        }
        for r in readings
    ]

