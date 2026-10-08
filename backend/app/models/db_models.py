from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, func
from backend.app.db.session import Base


class CameraSource(Base):
    __tablename__ = "camera_sources"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    bus_id = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(128), nullable=False)
    stream_url_or_path = Column(String(512), nullable=True)
    status = Column(String(32), default="STOPPED", nullable=False)  # STOPPED, RUNNING, PAUSED, ERROR
    is_active = Column(Boolean, default=False, nullable=False)
    fps = Column(Float, default=0.0, nullable=False)
    current_lat = Column(Float, nullable=True)
    current_lon = Column(Float, nullable=True)
    total_frames_processed = Column(Integer, default=0, nullable=False)
    total_incidents_detected = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)


class IncidentEvent(Base):
    __tablename__ = "incident_events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    event_uuid = Column(String(64), unique=True, index=True, nullable=False)
    event_type = Column(String(64), index=True, nullable=False)  # POTHOLE, CRACK, PROXIMITY_CONFLICT, RASH_DRIVING_CANDIDATE, etc.
    severity = Column(String(32), default="MEDIUM", nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    confidence = Column(Float, nullable=False)
    camera_id = Column(String(64), index=True, nullable=False)  # BUS-001, etc.
    track_id = Column(Integer, nullable=True)
    timestamp = Column(Float, nullable=False)  # Video / stream relative timestamp (seconds)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    is_simulated_gps = Column(Boolean, default=True, nullable=False)
    evidence_image_path = Column(String(512), nullable=True)
    review_status = Column(String(32), default="PENDING", index=True, nullable=False)  # PENDING, VERIFIED, FALSE_POSITIVE, RESOLVED
    review_notes = Column(Text, nullable=True)
    metadata_json = Column(Text, nullable=True)  # JSON payload for bbox, temporal rules details, etc.
    created_at = Column(DateTime, server_default=func.now(), nullable=False)


class VehicleCountRecord(Base):
    __tablename__ = "vehicle_count_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    camera_id = Column(String(64), index=True, nullable=False)
    vehicle_class = Column(String(64), nullable=False)  # car, bus, truck, motorcycle, bicycle
    count = Column(Integer, default=0, nullable=False)
    density_level = Column(String(32), default="LOW", nullable=False)  # LOW, MEDIUM, HIGH, CONGESTED
    time_window_start = Column(DateTime, nullable=False)
    time_window_end = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)


class ANPRReading(Base):
    __tablename__ = "anpr_readings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    camera_id = Column(String(64), index=True, nullable=False)
    track_id = Column(Integer, nullable=True)
    plate_text = Column(String(64), index=True, nullable=False)
    confidence = Column(Float, nullable=False)
    evidence_crop_path = Column(String(512), nullable=True)
    verification_status = Column(String(32), default="NEEDS_REVIEW", nullable=False)  # VERIFIED, NEEDS_REVIEW, REJECTED
    timestamp = Column(Float, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
