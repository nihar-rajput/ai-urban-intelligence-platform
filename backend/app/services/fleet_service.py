import asyncio
from typing import Dict
from sqlalchemy import select

from backend.app.core.logging import logger
from backend.app.db.session import AsyncSessionLocal
from backend.app.models.db_models import CameraSource
from backend.app.services.gps_simulator import SimulatedGPSEngine
from backend.app.services.tracking_service import fleet_tracker


class FleetSimulationService:
    """
    Manages continuous background lifecycle loops for BUS-001, BUS-002, BUS-003.
    Updates telemetry, coordinates, and simulated video playback timestamps.
    """

    def __init__(self):
        self._running_tasks: Dict[str, asyncio.Task] = {}
        self._stream_timestamps: Dict[str, float] = {
            "BUS-001": 0.0,
            "BUS-002": 0.0,
            "BUS-003": 0.0
        }

    async def _stream_worker(self, bus_id: str):
        logger.info(f"Background simulation worker started for {bus_id}")
        try:
            while True:
                await asyncio.sleep(1.0)
                self._stream_timestamps[bus_id] += 1.0
                curr_t = self._stream_timestamps[bus_id]

                lat, lon, speed = SimulatedGPSEngine.get_position(bus_id, curr_t)

                async with AsyncSessionLocal() as db:
                    result = await db.execute(select(CameraSource).where(CameraSource.bus_id == bus_id))
                    source = result.scalar_one_or_none()
                    if source and source.status == "RUNNING":
                        source.current_lat = lat
                        source.current_lon = lon
                        source.fps = 24.0
                        source.total_frames_processed += 24
                        await db.commit()
                    elif source and source.status != "RUNNING":
                        # If stopped or paused in DB, exit worker
                        break
        except asyncio.CancelledError:
            logger.info(f"Worker for {bus_id} cancelled.")
        except Exception as e:
            logger.error(f"Worker error for {bus_id}: {e}")

    def start_stream(self, bus_id: str):
        if bus_id in self._running_tasks and not self._running_tasks[bus_id].done():
            return
        task = asyncio.create_task(self._stream_worker(bus_id))
        self._running_tasks[bus_id] = task

    def pause_stream(self, bus_id: str):
        if bus_id in self._running_tasks:
            self._running_tasks[bus_id].cancel()

    def stop_stream(self, bus_id: str):
        if bus_id in self._running_tasks:
            self._running_tasks[bus_id].cancel()
        self._stream_timestamps[bus_id] = 0.0
        fleet_tracker.reset_tracker(bus_id)

    def replay_stream(self, bus_id: str):
        self.stop_stream(bus_id)
        self.start_stream(bus_id)


fleet_service = FleetSimulationService()
