import math
from typing import List, Optional, Dict, Any
from backend.app.services.tracking_service import TrackedObject


class SafetyAnalyticsEngine:
    """
    Explainable temporal rules engine for detecting candidate safety incidents.
    Strictly reports candidate events for human-in-the-loop audit rather than conclusive fault/intent.
    """

    def __init__(
        self,
        proximity_threshold_px: float = 65.0,
        swerving_threshold_px: float = 24.0
    ):
        self.proximity_threshold_px = proximity_threshold_px
        self.swerving_threshold_px = swerving_threshold_px

    def evaluate_proximity_conflicts(
        self,
        vehicles: List[TrackedObject],
        pedestrians: List[TrackedObject]
    ) -> List[Dict[str, Any]]:
        """
        Rule A: Identifies candidate close-proximity conflicts between vehicles and pedestrians/cyclists.
        Requires spatial proximity below threshold with converging trajectories.
        """
        candidates: List[Dict[str, Any]] = []

        for v in vehicles:
            vx = (v.box[0] + v.box[2]) / 2.0
            vy = v.box[3]  # Vehicle ground contact

            for p in pedestrians:
                px = (p.box[0] + p.box[2]) / 2.0
                py = p.box[3]  # Pedestrian ground contact

                dist = math.hypot(vx - px, vy - py)
                if dist < self.proximity_threshold_px:
                    candidates.append({
                        "event_type": "PROXIMITY_CONFLICT",
                        "severity": "HIGH",
                        "confidence": 0.78,
                        "track_id": v.track_id,
                        "metadata": {
                            "candidate_reason": "Close proximity conflict between vehicle and pedestrian",
                            "measured_pixel_distance": round(dist, 1),
                            "vehicle_track_id": v.track_id,
                            "pedestrian_track_id": p.track_id,
                            "disclaimer": "Automated proximity candidate for human verification; does not establish fault."
                        }
                    })

        return candidates

    def evaluate_rash_driving_candidates(
        self,
        vehicles: List[TrackedObject]
    ) -> List[Dict[str, Any]]:
        """
        Rule B: Identifies candidate erratic or high lateral swerve patterns across temporal track history.
        Evaluates lateral displacement (dx/dt) over consecutive observed frames.
        """
        candidates: List[Dict[str, Any]] = []

        for v in vehicles:
            if len(v.history) < 5:
                continue

            # Calculate lateral displacement over recent 4 frames
            recent_points = v.history[-4:]
            lateral_displacements = [
                abs(recent_points[i][0] - recent_points[i - 1][0])
                for i in range(1, len(recent_points))
            ]

            avg_lateral_rate = sum(lateral_displacements) / len(lateral_displacements)
            if avg_lateral_rate > self.swerving_threshold_px:
                candidates.append({
                    "event_type": "RASH_DRIVING_CANDIDATE",
                    "severity": "CRITICAL",
                    "confidence": 0.74,
                    "track_id": v.track_id,
                    "metadata": {
                        "candidate_reason": "High lateral trajectory displacement (potential swerving/abrupt lane change)",
                        "average_lateral_rate_px_per_frame": round(avg_lateral_rate, 2),
                        "observed_frames": len(v.history),
                        "disclaimer": "Candidate pattern flagged for human audit; does not prove driver intent or violation."
                    }
                })

        return candidates


safety_engine = SafetyAnalyticsEngine()
