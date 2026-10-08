import os
import cv2
import numpy as np
import pytest
from backend.app.db.session import AsyncSessionLocal
from backend.app.services.gps_simulator import SimulatedGPSEngine
from backend.app.services.inference_service import inference_engine, DetectionResult
from backend.app.services.event_service import event_engine
from backend.app.services.video_service import video_service


def test_gps_interpolation():
    lat, lon, speed = SimulatedGPSEngine.get_position("BUS-001", 10.0)
    # Check bounds around Delhi region (lat ~ 28.5 to 28.7, lon ~ 77.1 to 77.3)
    assert 28.5 <= lat <= 28.7
    assert 77.1 <= lon <= 77.3
    assert 20.0 <= speed <= 60.0


def test_inference_engine_detectors():
    # Create test synthetic frame with gray asphalt
    frame = np.full((720, 1280, 3), 50, dtype=np.uint8)
    # Draw dark simulated depression
    cv2.ellipse(frame, (600, 500), (35, 18), 0, 0, 360, (15, 15, 15), -1)

    # Run vehicle detector
    v_dets = inference_engine.detect_vehicles(frame)
    assert isinstance(v_dets, list)

    # Run defect detector
    d_dets = inference_engine.detect_road_defects(frame)
    assert isinstance(d_dets, list)
    assert len(d_dets) >= 1
    assert d_dets[0].class_name == "POTHOLE"


@pytest.mark.asyncio
async def test_event_deduplication_and_persistence():
    async with AsyncSessionLocal() as db:
        frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        det = DetectionResult(
            box=[550, 480, 650, 520],
            class_name="POTHOLE",
            confidence=0.78,
            detector_source="HEURISTIC_PREVIEW"
        )

        # 1st detection should create an incident
        inc1 = await event_engine.create_incident(
            db=db,
            camera_id="BUS-001",
            detection=det,
            frame=frame,
            timestamp_sec=2.5
        )
        assert inc1 is not None
        assert inc1.event_type == "POTHOLE"
        assert inc1.is_simulated_gps is True
        assert inc1.camera_id == "BUS-001"

        # 2nd detection immediately after (t=2.6s) should be blocked by cooldown
        inc2 = await event_engine.create_incident(
            db=db,
            camera_id="BUS-001",
            detection=det,
            frame=frame,
            timestamp_sec=2.6
        )
        assert inc2 is None  # Blocked by cooldown!


@pytest.mark.asyncio
async def test_video_service_vertical_slice():
    video_path = "sample_videos/demo_road_run.mp4"
    assert os.path.exists(video_path), "Demo road video must exist before running test"

    async with AsyncSessionLocal() as db:
        result = await video_service.process_video(
            video_path=video_path,
            camera_id="BUS-001",
            db=db,
            max_frames=30
        )

        assert result["status"] == "completed"
        assert result["frames_processed"] == 30
        assert result["processing_fps"] > 0
        assert os.path.exists(result["annotated_video_path"])
