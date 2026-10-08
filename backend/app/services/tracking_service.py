from typing import List, Dict, Tuple, Optional, Set
import numpy as np
from dataclasses import dataclass, field
from backend.app.services.inference_service import DetectionResult


@dataclass
class TrackedObject:
    track_id: int
    class_name: str
    box: List[int]  # [x1, y1, x2, y2]
    confidence: float
    hits: int = 1
    age: int = 1
    time_since_update: int = 0
    history: List[Tuple[int, int]] = field(default_factory=list)  # [(center_x, center_y), ...]


def compute_iou(boxA: List[int], boxB: List[int]) -> float:
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    interW = max(0, xB - xA)
    interH = max(0, yB - yA)
    interArea = interW * interH

    boxAArea = max(0, boxA[2] - boxA[0]) * max(0, boxA[3] - boxA[1])
    boxBArea = max(0, boxB[2] - boxB[0]) * max(0, boxB[3] - boxB[1])

    unionArea = float(boxAArea + boxBArea - interArea)
    if unionArea <= 0:
        return 0.0
    return interArea / unionArea


class StreamTracker:
    """
    Independent multi-object tracker for a single camera stream.
    Associates detections across consecutive frames using spatial IoU matching and track persistence,
    assigning stable Track IDs and preventing duplicate vehicle counting.
    """

    def __init__(
        self,
        camera_id: str,
        max_age: int = 15,
        min_hits: int = 2,
        iou_threshold: float = 0.30
    ):
        self.camera_id = camera_id
        self.max_age = max_age
        self.min_hits = min_hits
        self.iou_threshold = iou_threshold

        self._next_id = 1
        self.tracked_objects: Dict[int, TrackedObject] = {}

        # Vehicle Counting State (ensures zero double-counting)
        self.counted_track_ids: Set[int] = set()
        self.counts_by_class: Dict[str, int] = {
            "car": 0,
            "bus": 0,
            "truck": 0,
            "motorcycle": 0,
            "bicycle": 0,
            "person": 0
        }

    def update(self, detections: List[DetectionResult], frame_shape: Tuple[int, int]) -> List[DetectionResult]:
        """
        Updates tracking state with new frame detections.
        Matches existing tracks to detections, creates new tracks, expires stale tracks,
        and counts newly confirmed vehicles without repetition.
        """
        # Age existing tracks
        for obj in self.tracked_objects.values():
            obj.age += 1
            obj.time_since_update += 1

        matched_tracks: Set[int] = set()
        matched_detections: Set[int] = set()

        # Match detections to existing tracks via IoU
        if self.tracked_objects and detections:
            track_ids = list(self.tracked_objects.keys())
            iou_matrix = np.zeros((len(track_ids), len(detections)), dtype=np.float32)

            for i, tid in enumerate(track_ids):
                for j, det in enumerate(detections):
                    # Same or compatible class preference
                    if det.class_name == self.tracked_objects[tid].class_name:
                        iou_matrix[i, j] = compute_iou(self.tracked_objects[tid].box, det.box)
                    else:
                        iou_matrix[i, j] = compute_iou(self.tracked_objects[tid].box, det.box) * 0.5

            # Greedy Hungarian-style matching
            while True:
                if iou_matrix.size == 0:
                    break
                max_iou = np.max(iou_matrix)
                if max_iou < self.iou_threshold:
                    break
                idx = np.unravel_index(np.argmax(iou_matrix), iou_matrix.shape)
                i, j = idx[0], idx[1]

                tid = track_ids[i]
                det = detections[j]

                # Update track with matched detection
                t_obj = self.tracked_objects[tid]
                t_obj.box = det.box
                t_obj.confidence = det.confidence
                t_obj.hits += 1
                t_obj.time_since_update = 0
                cx = (det.box[0] + det.box[2]) // 2
                cy = (det.box[1] + det.box[3]) // 2
                t_obj.history.append((cx, cy))
                if len(t_obj.history) > 30:
                    t_obj.history.pop(0)

                det.track_id = tid
                matched_tracks.add(tid)
                matched_detections.add(j)

                # Invalidate matched row and column
                iou_matrix[i, :] = -1
                iou_matrix[:, j] = -1

        # Create new tracks for unmatched detections
        for j, det in enumerate(detections):
            if j not in matched_detections:
                new_tid = self._next_id
                self._next_id += 1

                cx = (det.box[0] + det.box[2]) // 2
                cy = (det.box[1] + det.box[3]) // 2

                self.tracked_objects[new_tid] = TrackedObject(
                    track_id=new_tid,
                    class_name=det.class_name,
                    box=det.box,
                    confidence=det.confidence,
                    hits=1,
                    age=1,
                    time_since_update=0,
                    history=[(cx, cy)]
                )
                det.track_id = new_tid

        # Remove dead / stale tracks
        expired = [tid for tid, obj in self.tracked_objects.items() if obj.time_since_update > self.max_age]
        for tid in expired:
            del self.tracked_objects[tid]

        # Vehicle Counting Logic:
        # A vehicle is counted when it reaches min_hits (confirmed track) and has not been counted before
        for tid, obj in self.tracked_objects.items():
            if obj.hits >= self.min_hits and tid not in self.counted_track_ids:
                self.counted_track_ids.add(tid)
                cls_lower = obj.class_name.lower()
                self.counts_by_class[cls_lower] = self.counts_by_class.get(cls_lower, 0) + 1

        return detections

    def get_traffic_density(self) -> str:
        """Estimates traffic density level from active vehicles in frame."""
        active_vehicles = sum(
            1 for obj in self.tracked_objects.values()
            if obj.time_since_update == 0 and obj.class_name in ["car", "bus", "truck", "motorcycle"]
        )
        if active_vehicles <= 2:
            return "LOW"
        elif active_vehicles <= 5:
            return "MEDIUM"
        elif active_vehicles <= 8:
            return "HIGH"
        else:
            return "CONGESTED"

    def get_stats(self) -> Dict:
        return {
            "camera_id": self.camera_id,
            "active_tracks": len([o for o in self.tracked_objects.values() if o.time_since_update == 0]),
            "total_unique_vehicles": len(self.counted_track_ids),
            "counts_by_class": dict(self.counts_by_class),
            "density_level": self.get_traffic_density()
        }


class FleetTrackingManager:
    """
    Manages isolated, independent tracker instances for BUS-001, BUS-002, BUS-003, etc.
    Guarantees no state leakage between separate camera streams.
    """

    def __init__(self):
        self._trackers: Dict[str, StreamTracker] = {}

    def get_tracker(self, camera_id: str) -> StreamTracker:
        if camera_id not in self._trackers:
            self._trackers[camera_id] = StreamTracker(camera_id=camera_id)
        return self._trackers[camera_id]

    def reset_tracker(self, camera_id: str):
        self._trackers[camera_id] = StreamTracker(camera_id=camera_id)


fleet_tracker = FleetTrackingManager()
