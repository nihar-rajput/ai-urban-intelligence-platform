from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from backend.app.db.session import get_db
from backend.app.models.db_models import IncidentEvent
from backend.app.schemas.events import (
    IncidentEventRead,
    IncidentEventCreate,
    IncidentReviewUpdate
)
import uuid

router = APIRouter(prefix="/events", tags=["Incident Events"])


@router.get("", response_model=List[IncidentEventRead])
async def list_incident_events(
    camera_id: Optional[str] = Query(None, description="Filter by camera/bus ID"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    severity: Optional[str] = Query(None, description="Filter by severity level"),
    review_status: Optional[str] = Query(None, description="Filter by review status"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve paginated and filtered list of incident events."""
    query = select(IncidentEvent)

    if camera_id:
        query = query.where(IncidentEvent.camera_id == camera_id)
    if event_type:
        query = query.where(IncidentEvent.event_type == event_type)
    if severity:
        query = query.where(IncidentEvent.severity == severity.upper())
    if review_status:
        query = query.where(IncidentEvent.review_status == review_status.upper())

    query = query.order_by(desc(IncidentEvent.created_at)).offset(offset).limit(limit)
    result = await db.execute(query)
    events = result.scalars().all()
    return [IncidentEventRead.model_validate(e) for e in events]


@router.get("/{event_id}", response_model=IncidentEventRead)
async def get_incident_event(event_id: int, db: AsyncSession = Depends(get_db)):
    """Retrieve detailed information for a specific incident."""
    result = await db.execute(select(IncidentEvent).where(IncidentEvent.id == event_id))
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident event #{event_id} not found."
        )
    return IncidentEventRead.model_validate(event)


@router.patch("/{event_id}/review", response_model=IncidentEventRead)
async def update_incident_review(
    event_id: int,
    review_data: IncidentReviewUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Human-in-the-loop review action: verify, mark as false positive, or resolve."""
    result = await db.execute(select(IncidentEvent).where(IncidentEvent.id == event_id))
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident event #{event_id} not found."
        )

    allowed_statuses = ["PENDING", "VERIFIED", "FALSE_POSITIVE", "RESOLVED"]
    status_upper = review_data.review_status.upper()
    if status_upper not in allowed_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid review status. Choose from: {allowed_statuses}"
        )

    event.review_status = status_upper
    if review_data.review_notes is not None:
        event.review_notes = review_data.review_notes

    await db.commit()
    await db.refresh(event)
    return IncidentEventRead.model_validate(event)


@router.post("", response_model=IncidentEventRead, status_code=status.HTTP_201_CREATED)
async def create_incident_event(
    event_in: IncidentEventCreate,
    db: AsyncSession = Depends(get_db)
):
    """Internal or detector ingestion endpoint to persist a newly detected incident."""
    event = IncidentEvent(
        event_uuid=event_in.event_uuid or f"EVT-{uuid.uuid4().hex[:10].upper()}",
        event_type=event_in.event_type.upper(),
        severity=event_in.severity.upper(),
        confidence=event_in.confidence,
        camera_id=event_in.camera_id,
        track_id=event_in.track_id,
        timestamp=event_in.timestamp,
        latitude=event_in.latitude,
        longitude=event_in.longitude,
        is_simulated_gps=event_in.is_simulated_gps,
        evidence_image_path=event_in.evidence_image_path,
        review_status=event_in.review_status.upper(),
        review_notes=event_in.review_notes,
        metadata_json=event_in.metadata_json
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return IncidentEventRead.model_validate(event)
