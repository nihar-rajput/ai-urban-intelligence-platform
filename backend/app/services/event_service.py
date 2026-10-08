import os
import json
import uuid
from typing import Optional, Dict, Tuple, Any
import cv2
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.models.db_models import IncidentEvent, CameraSource
from backend.app.services.gps_simulator import SimulatedGPSEngine
from backend.app.services.inference_service import DetectionResult


class EventProcessingEngine:
    """
    Converts raw computer vision detections into structured incident events.
    Applies spatial-temporal deduplication and cooldowns to prevent frame-by-frame alert flooding.
    """

    def __init__(self, cooldown_seconds: float = 3.0):
        self.cooldown_seconds = cooldown_seconds
        # Tracks last alert timestamp per (camera_id, event_type): float
        self._last_alert_time: Dict[Tuple[str, str], float] = {}

    def should_emit_alert(self, camera_id: str, event_type: str, current_timestamp: float) -> bool:
        """Enforces cooldown window per camera and event type."""
        key = (camera_id, event_type.upper())
        last_time = self._last_alert_time.get(key, -999.0)
        if current_timestamp - last_time >= self.cooldown_seconds:
            self._last_alert_time[key] = current_timestamp
            return True
        return False

    def save_evidence_crop(
        self,
        frame: np.ndarray,
        box: list,
        event_uuid: str
    ) -> Optional[str]:
        """Crops detection bounding box with padding and saves to evidence storage."""
        try:
            h, w = frame.shape[:2]
            x1, y1, x2, y2 = box
            # Add 15% padding
            pad_x = int((x2 - x1) * 0.15)
            pad_y = int((y2 - y1) * 0.15)

            crop_x1 = max(0, x1 - pad_x)
            crop_y1 = max(0, y1 - pad_y)
            crop_x2 = min(w, x2 + pad_x)
            crop_y2 = min(h, y2 + pad_y)

            crop = frame[crop_y1:crop_y2, crop_x1:crop_x2]
            if crop.size == 0:
                return None

            os.makedirs(settings.STORAGE_DIR, exist_ok=True)
            filename = f"evidence_{event_uuid}.jpg"
            dest_path = os.path.join(settings.STORAGE_DIR, filename)
            cv2.imwrite(dest_path, crop)
            return f"evidence/{filename}"
        except Exception as e:
            logger.error(f"Failed to save evidence crop: {e}")
            return None

    async def create_incident(
        self,
        db: AsyncSession,
        camera_id: str,
        detection: DetectionResult,
        frame: np.ndarray,
        timestamp_sec: float,
        custom_metadata: Optional[Dict[str, Any]] = None,
        custom_severity: Optional[str] = None
    ) -> Optional[IncidentEvent]:
        """Process detection, check deduplication, attach simulated GPS, and store incident."""
        event_type = detection.class_name.upper()

        # Cooldown check
        if not self.should_emit_alert(camera_id, event_type, timestamp_sec):
            return None

        # Severity determination
        severity = custom_severity or "MEDIUM"
        if not custom_severity:
            if event_type in ["POTHOLE", "ROAD_DAMAGE", "COLLISION_RISK"]:
                severity = "HIGH" if detection.confidence > 0.65 else "MEDIUM"
            elif event_type in ["RASH_DRIVING_CANDIDATE", "SEVERE_CONFLICT", "PROXIMITY_CONFLICT"]:
                severity = "CRITICAL"

        event_uuid = f"EVT-{uuid.uuid4().hex[:10].upper()}"
        evidence_path = self.save_evidence_crop(frame, detection.box, event_uuid)

        # Obtain simulated GPS position
        lat, lon, speed = SimulatedGPSEngine.get_position(camera_id, timestamp_sec)

        metadata = {
            "bounding_box": detection.box,
            "detector_source": detection.detector_source,
            "simulated_speed_kmh": speed,
            "track_id": detection.track_id
        }
        if custom_metadata:
            metadata.update(custom_metadata)

        incident = IncidentEvent(
            event_uuid=event_uuid,
            event_type=event_type,
            severity=severity,
            confidence=detection.confidence,
            camera_id=camera_id,
            track_id=detection.track_id,
            timestamp=round(timestamp_sec, 2),
            latitude=lat,
            longitude=lon,
            is_simulated_gps=True,
            evidence_image_path=evidence_path,
            review_status="PENDING",
            metadata_json=json.dumps(metadata)
        )

        db.add(incident)
        await db.commit()
        await db.refresh(incident)

        logger.info(f"New incident logged: {incident.event_type} [{incident.severity}] on {camera_id} at {lat},{lon}")

        # Broadcast real-time WebSocket alert
        try:
            from backend.app.services.websocket_manager import ws_manager
            await ws_manager.broadcast_alert({
                "type": "INCIDENT_ALERT",
                "data": {
                    "id": incident.id,
                    "event_uuid": incident.event_uuid,
                    "event_type": incident.event_type,
                    "severity": incident.severity,
                    "confidence": incident.confidence,
                    "camera_id": incident.camera_id,
                    "track_id": incident.track_id,
                    "timestamp": incident.timestamp,
                    "latitude": incident.latitude,
                    "longitude": incident.longitude,
                    "is_simulated_gps": incident.is_simulated_gps,
                    "evidence_image_path": incident.evidence_image_path,
                    "review_status": incident.review_status,
                    "created_at": incident.created_at.isoformat() if incident.created_at else None
                }
            })
        except Exception as ws_err:
            logger.warning(f"Failed to broadcast alert over WebSocket: {ws_err}")

        return incident


event_engine = EventProcessingEngine(cooldown_seconds=2.5)
