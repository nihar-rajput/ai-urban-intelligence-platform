import pytest
import numpy as np
from httpx import AsyncClient, ASGITransport

from backend.app.main import app
from backend.app.services.safety_service import SafetyAnalyticsEngine
from backend.app.services.tracking_service import TrackedObject
from backend.app.services.anpr_service import ANPREngine


def test_safety_proximity_conflict_detection():
    """Verify explainable proximity conflict flagged when vehicle and pedestrian are within threshold."""
    engine = SafetyAnalyticsEngine(proximity_threshold_px=70.0)

    # Vehicle at ground point (100, 200)
    vehicle = TrackedObject(
        track_id=1,
        class_name="car",
        box=[80, 150, 120, 200],
        confidence=0.88,
        history=[(100, 180), (100, 200)]
    )

    # Pedestrian close at ground point (110, 215) -> dist ~= 18px < 70px
    pedestrian = TrackedObject(
        track_id=2,
        class_name="person",
        box=[105, 180, 115, 215],
        confidence=0.82,
        history=[(110, 200), (110, 215)]
    )

    candidates = engine.evaluate_proximity_conflicts([vehicle], [pedestrian])
    assert len(candidates) == 1
    c = candidates[0]
    assert c["event_type"] == "PROXIMITY_CONFLICT"
    assert c["severity"] == "HIGH"
    assert "disclaimer" in c["metadata"]
    assert "does not establish fault" in c["metadata"]["disclaimer"].lower()


def test_safety_proximity_safe_distance():
    """Verify no candidate flagged when entities maintain safe clearance."""
    engine = SafetyAnalyticsEngine(proximity_threshold_px=50.0)

    vehicle = TrackedObject(
        track_id=1,
        class_name="car",
        box=[50, 50, 100, 100],
        confidence=0.9
    )
    pedestrian = TrackedObject(
        track_id=2,
        class_name="person",
        box=[300, 300, 350, 400],
        confidence=0.85
    )

    candidates = engine.evaluate_proximity_conflicts([vehicle], [pedestrian])
    assert len(candidates) == 0


def test_safety_rash_driving_swerving_candidate():
    """Verify erratic lateral swerving triggers candidate review alert."""
    engine = SafetyAnalyticsEngine(swerving_threshold_px=20.0)

    # Vehicle with rapid lateral shifts: x jumps 100 -> 140 -> 90 -> 150 -> 80
    vehicle = TrackedObject(
        track_id=5,
        class_name="car",
        box=[80, 200, 140, 280],
        confidence=0.87,
        history=[(100, 100), (145, 120), (90, 140), (155, 160), (80, 180)]
    )

    candidates = engine.evaluate_rash_driving_candidates([vehicle])
    assert len(candidates) == 1
    c = candidates[0]
    assert c["event_type"] == "RASH_DRIVING_CANDIDATE"
    assert c["severity"] == "CRITICAL"
    assert "disclaimer" in c["metadata"]
    assert "human audit" in c["metadata"]["disclaimer"].lower()


def test_safety_stable_driving_no_alert():
    """Verify straight trajectory vehicle does not generate swerving alerts."""
    engine = SafetyAnalyticsEngine(swerving_threshold_px=20.0)

    vehicle = TrackedObject(
        track_id=6,
        class_name="car",
        box=[190, 200, 250, 280],
        confidence=0.92,
        history=[(200, 100), (202, 120), (201, 140), (203, 160), (202, 180)]
    )

    candidates = engine.evaluate_rash_driving_candidates([vehicle])
    assert len(candidates) == 0


def test_anpr_engine_plate_localization_and_format():
    """Verify ANPR plate extraction, standard regex matching, and review tagging."""
    engine = ANPREngine()

    # Create dummy vehicle crop (200x200 RGB) with synthetic white rectangular plate in lower region
    crop = np.zeros((200, 200, 3), dtype=np.uint8)
    crop[:, :] = (120, 120, 120)  # Gray car body
    # Lower third plate region
    crop[140:170, 50:150] = (255, 255, 255)  # White plate rectangle

    reading = engine.read_plate(crop, camera_id="BUS-001", track_id=12, timestamp_sec=4.5)
    assert reading is not None
    assert reading["camera_id"] == "BUS-001"
    assert reading["track_id"] == 12
    assert reading["verification_status"] in ["VERIFIED", "NEEDS_REVIEW"]
    assert reading["plate_text"] is not None
    assert len(reading["plate_text"]) > 4


@pytest.mark.asyncio
async def test_anpr_api_endpoint():
    """Verify GET /api/v1/analytics/anpr returns structured array."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/analytics/anpr?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
