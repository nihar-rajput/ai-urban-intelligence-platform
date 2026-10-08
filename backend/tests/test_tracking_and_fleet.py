import pytest
from backend.app.services.tracking_service import StreamTracker, FleetTrackingManager, fleet_tracker
from backend.app.services.inference_service import DetectionResult


def test_independent_stream_trackers():
    manager = FleetTrackingManager()
    tracker1 = manager.get_tracker("BUS-001")
    tracker2 = manager.get_tracker("BUS-002")

    det1 = [DetectionResult(box=[100, 100, 200, 200], class_name="car", confidence=0.85, detector_source="test")]
    tracker1.update(det1, (720, 1280))

    # BUS-001 should have track_id=1
    assert 1 in tracker1.tracked_objects
    assert len(tracker1.tracked_objects) == 1

    # BUS-002 should have 0 tracks (completely isolated)
    assert len(tracker2.tracked_objects) == 0


def test_unique_vehicle_counting_no_duplicates():
    tracker = StreamTracker(camera_id="BUS-001", min_hits=2)

    # Frame 1: Car appears at (100, 100)
    det_f1 = [DetectionResult(box=[100, 100, 200, 200], class_name="car", confidence=0.90, detector_source="test")]
    tracker.update(det_f1, (720, 1280))
    # Hits = 1 (less than min_hits=2), not counted yet
    assert tracker.counts_by_class["car"] == 0

    # Frame 2: Car moves slightly to (105, 105) (matched to track 1, hits=2)
    det_f2 = [DetectionResult(box=[105, 105, 205, 205], class_name="car", confidence=0.92, detector_source="test")]
    tracker.update(det_f2, (720, 1280))
    # Hits = 2 -> Confirmed and counted once!
    assert tracker.counts_by_class["car"] == 1
    assert len(tracker.counted_track_ids) == 1

    # Frames 3 through 10: Car continues moving
    for step in range(3, 11):
        x = 100 + step * 5
        det_fn = [DetectionResult(box=[x, x, x + 100, x + 100], class_name="car", confidence=0.91, detector_source="test")]
        tracker.update(det_fn, (720, 1280))

    # Should STILL BE 1 count, never double-counted!
    assert tracker.counts_by_class["car"] == 1
    assert len(tracker.counted_track_ids) == 1


def test_traffic_density_levels():
    tracker = StreamTracker(camera_id="BUS-001")
    assert tracker.get_traffic_density() == "LOW"

    # Add 4 active vehicles
    for i in range(4):
        tracker.tracked_objects[i + 1] = DetectionResult(
            box=[i * 50, 100, i * 50 + 40, 140],
            class_name="car",
            confidence=0.88,
            detector_source="test"
        )
        # Set dummy attributes for TrackedObject
        tracker.tracked_objects[i + 1].time_since_update = 0

    assert tracker.get_traffic_density() == "MEDIUM"


def test_stream_tracker_expiry():
    tracker = StreamTracker(camera_id="BUS-001", max_age=5)
    det = [DetectionResult(box=[100, 100, 200, 200], class_name="car", confidence=0.90, detector_source="test")]
    tracker.update(det, (720, 1280))
    assert len(tracker.tracked_objects) == 1

    # Pass empty frames for 6 frames (> max_age 5)
    for _ in range(6):
        tracker.update([], (720, 1280))

    # Track should be cleanly expired
    assert len(tracker.tracked_objects) == 0
