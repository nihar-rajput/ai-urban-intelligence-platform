from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.db.session import get_db
from backend.app.models.db_models import CameraSource
from backend.app.schemas.fleet import (
    CameraSourceRead,
    StreamControlCommand,
    FleetStatusSummary
)
from backend.app.core.config import settings
from backend.app.core.logging import logger

router = APIRouter(prefix="/fleet", tags=["Fleet & Camera Sources"])


async def ensure_default_fleet_sources(db: AsyncSession):
    """Ensure BUS-001, BUS-002, and BUS-003 exist in the database."""
    default_buses = [
        {"bus_id": "BUS-001", "name": "Bus Route 101 - Connaught Place to AIIMS", "lat": 28.6139, "lon": 77.2090},
        {"bus_id": "BUS-002", "name": "Bus Route 204 - Nehru Place to Lajpat Nagar", "lat": 28.5494, "lon": 77.2534},
        {"bus_id": "BUS-003", "name": "Bus Route 305 - Red Fort to ISBT Kashmere Gate", "lat": 28.6562, "lon": 77.2410},
    ]

    for item in default_buses:
        result = await db.execute(select(CameraSource).where(CameraSource.bus_id == item["bus_id"]))
        existing = result.scalar_one_or_none()
        if not existing:
            source = CameraSource(
                bus_id=item["bus_id"],
                name=item["name"],
                status="STOPPED",
                is_active=False,
                fps=0.0,
                current_lat=item["lat"],
                current_lon=item["lon"],
                total_frames_processed=0,
                total_incidents_detected=0
            )
            db.add(source)
    await db.commit()


@router.get("", response_model=FleetStatusSummary)
async def get_fleet_status(db: AsyncSession = Depends(get_db)):
    """Retrieve full fleet status summary and all camera sources."""
    await ensure_default_fleet_sources(db)
    result = await db.execute(select(CameraSource).order_by(CameraSource.bus_id))
    sources = result.scalars().all()

    total = len(sources)
    active = sum(1 for s in sources if s.is_active or s.status == "RUNNING")
    stopped = total - active

    return FleetStatusSummary(
        total_buses=total,
        active_buses=active,
        stopped_buses=stopped,
        sources=[CameraSourceRead.model_validate(s) for s in sources]
    )


@router.get("/{bus_id}", response_model=CameraSourceRead)
async def get_bus_status(bus_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieve the status and telemetry of an individual bus camera stream."""
    result = await db.execute(select(CameraSource).where(CameraSource.bus_id == bus_id))
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bus source '{bus_id}' not found."
        )
    return CameraSourceRead.model_validate(source)


@router.post("/{bus_id}/control", response_model=CameraSourceRead)
async def control_bus_stream(
    bus_id: str,
    command: StreamControlCommand,
    db: AsyncSession = Depends(get_db)
):
    """Execute START, PAUSE, RESUME, STOP, or REPLAY for a bus camera source."""
    result = await db.execute(select(CameraSource).where(CameraSource.bus_id == bus_id))
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bus source '{bus_id}' not found."
        )

    action = command.action.upper()
    valid_actions = ["START", "PAUSE", "RESUME", "STOP", "REPLAY"]
    if action not in valid_actions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid action '{action}'. Valid actions: {valid_actions}"
        )

    from backend.app.services.fleet_service import fleet_service

    if action == "START":
        source.status = "RUNNING"
        source.is_active = True
        source.fps = 24.0
        if command.video_path:
            source.stream_url_or_path = command.video_path
        fleet_service.start_stream(bus_id)
    elif action == "PAUSE":
        source.status = "PAUSED"
        source.is_active = False
        source.fps = 0.0
        fleet_service.pause_stream(bus_id)
    elif action == "RESUME":
        source.status = "RUNNING"
        source.is_active = True
        source.fps = 24.0
        fleet_service.start_stream(bus_id)
    elif action == "STOP":
        source.status = "STOPPED"
        source.is_active = False
        source.fps = 0.0
        fleet_service.stop_stream(bus_id)
    elif action == "REPLAY":
        source.status = "RUNNING"
        source.is_active = True
        source.fps = 24.0
        source.total_frames_processed = 0
        fleet_service.replay_stream(bus_id)

    await db.commit()
    await db.refresh(source)
    logger.info(f"Stream {bus_id} action '{action}' executed. Status: {source.status}")
    return CameraSourceRead.model_validate(source)
