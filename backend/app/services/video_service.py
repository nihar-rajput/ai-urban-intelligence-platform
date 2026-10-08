import os
import time
from datetime import datetime
from typing import Dict, Any, Optional, Set, List
import cv2
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.models.db_models import CameraSource, VehicleCountRecord, ANPRReading
from backend.app.services.inference_service import inference_engine, DetectionResult
from backend.app.services.event_service import event_engine
from backend.app.services.gps_simulator import SimulatedGPSEngine
from backend.app.services.tracking_service import fleet_tracker
from backend.app.services.safety_service import safety_engine
from backend.app.services.anpr_service import anpr_engine


class VideoProcessingService:
    """
    Decodes video streams, applies neural object detection & road defect analysis,
    tracks vehicles, evaluates candidate safety events, performs ANPR,
    draws telemetry annotations, extracts evidence crops, and renders annotated video output.
    """

    @staticmethod
    def draw_annotations(
        frame: np.ndarray,
        detections: list[DetectionResult],
        camera_id: str,
        timestamp_sec: float,
        lat: float,
        lon: float,
        speed_kmh: float
    ) -> np.ndarray:
        annotated = frame.copy()
        h, w = annotated.shape[:2]

        # Draw Detection Bounding Boxes
        for det in detections:
            x1, y1, x2, y2 = det.box
            is_defect = det.class_name.upper() in ["POTHOLE", "CRACK", "ROAD_DAMAGE"]
            is_safety_candidate = det.class_name.upper() in ["RASH_DRIVING_CANDIDATE", "PROXIMITY_CONFLICT"]

            if is_safety_candidate:
                box_color = (210, 50, 210)  # Magenta/Purple for candidate safety audit
            elif is_defect:
                box_color = (0, 0, 240)    # Red for road defect
            else:
                box_color = (240, 160, 20)  # Cyan/Orange for vehicle

            # Bounding box
            cv2.rectangle(annotated, (x1, y1), (x2, y2), box_color, 2)

            # Label badge with Track ID if available
            tid_str = f"#{det.track_id} " if det.track_id else ""
            if is_safety_candidate:
                label = f"{tid_str}AUDIT: {det.class_name.upper()} {int(det.confidence * 100)}%"
            else:
                label = f"{tid_str}{det.class_name.upper()} {int(det.confidence * 100)}%"
            font_scale = 0.5
            thickness = 1
            (lbl_w, lbl_h), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)

            badge_y1 = max(0, y1 - lbl_h - 8)
            badge_y2 = y1
            cv2.rectangle(annotated, (x1, badge_y1), (x1 + lbl_w + 10, badge_y2), box_color, -1)
            cv2.putText(
                annotated,
                label,
                (x1 + 5, y1 - 4),
                cv2.FONT_HERSHEY_SIMPLEX,
                font_scale,
                (255, 255, 255),
                thickness,
                cv2.LINE_AA
            )

        # Draw HUD Telemetry Header Bar
        cv2.rectangle(annotated, (0, 0), (w, 42), (15, 20, 30), -1)
        hud_text = (
            f"FLEET: {camera_id} | T: {timestamp_sec:.2f}s | "
            f"SIM GPS: {lat:.4f}, {lon:.4f} | SPEED: {speed_kmh:.1f} km/h | "
            f"OBJS: {len(detections)}"
        )
        cv2.putText(
            annotated,
            hud_text,
            (16, 26),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 230, 255),
            1,
            cv2.LINE_AA
        )

        return annotated

    async def process_video(
        self,
        video_path: str,
        camera_id: str,
        db: AsyncSession,
        max_frames: Optional[int] = None
    ) -> Dict[str, Any]:
        """Runs end-to-end inference and event generation on a target video."""
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found at: {video_path}")

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_video_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        os.makedirs(settings.STORAGE_DIR, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        output_filename = f"annotated_{base_name}_{camera_id}.mp4"
        output_path = os.path.join(settings.STORAGE_DIR, output_filename)

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        frame_count = 0
        incidents_created = 0
        anpr_processed_tracks: Set[int] = set()
        start_time = time.time()

        logger.info(f"Starting video processing: {video_path} on {camera_id} ({total_video_frames} frames)")

        try:
            while cap.isOpened():
                if max_frames and frame_count >= max_frames:
                    break

                ret, frame = cap.read()
                if not ret:
                    break

                frame_count += 1
                timestamp_sec = frame_count / fps
                lat, lon, speed = SimulatedGPSEngine.get_position(camera_id, timestamp_sec)

                # Run Detectors
                vehicle_dets = inference_engine.detect_vehicles(frame)
                defect_dets = inference_engine.detect_road_defects(frame)

                # Run Multi-Object Tracker on Vehicles (Isolated per camera stream)
                tracker = fleet_tracker.get_tracker(camera_id)
                vehicle_dets = tracker.update(vehicle_dets, (height, width))
                all_dets = list(vehicle_dets) + list(defect_dets)

                # 1. Evaluate Incidents for Road Defects
                for defect in defect_dets:
                    inc = await event_engine.create_incident(
                        db=db,
                        camera_id=camera_id,
                        detection=defect,
                        frame=frame,
                        timestamp_sec=timestamp_sec
                    )
                    if inc:
                        incidents_created += 1

                # 2. Evaluate Candidate Safety Events (Proximity & Rash Driving)
                active_vehicles = [
                    obj for obj in tracker.tracked_objects.values()
                    if obj.time_since_update == 0 and obj.class_name in ["car", "bus", "truck", "motorcycle"]
                ]
                active_pedestrians = [
                    obj for obj in tracker.tracked_objects.values()
                    if obj.time_since_update == 0 and obj.class_name in ["person", "bicycle"]
                ]

                safety_candidates = (
                    safety_engine.evaluate_proximity_conflicts(active_vehicles, active_pedestrians) +
                    safety_engine.evaluate_rash_driving_candidates(active_vehicles)
                )

                for cand in safety_candidates:
                    cand_tid = cand["track_id"]
                    cand_obj = tracker.tracked_objects.get(cand_tid)
                    cand_box = cand_obj.box if cand_obj else [0, 0, 80, 80]

                    cand_det = DetectionResult(
                        box=cand_box,
                        class_name=cand["event_type"],
                        confidence=cand["confidence"],
                        detector_source="SAFETY_ANALYTICS_ENGINE",
                        track_id=cand_tid
                    )
                    all_dets.append(cand_det)

                    inc = await event_engine.create_incident(
                        db=db,
                        camera_id=camera_id,
                        detection=cand_det,
                        frame=frame,
                        timestamp_sec=timestamp_sec,
                        custom_metadata=cand.get("metadata"),
                        custom_severity=cand.get("severity")
                    )
                    if inc:
                        incidents_created += 1

                # 3. Automatic Number Plate Recognition (ANPR) on confirmed vehicle tracks
                for v_det in vehicle_dets:
                    if (
                        v_det.track_id is not None
                        and v_det.track_id not in anpr_processed_tracks
                        and v_det.class_name in ["car", "bus", "truck"]
                    ):
                        vx1, vy1, vx2, vy2 = v_det.box
                        v_crop = frame[max(0, vy1):min(height, vy2), max(0, vx1):min(width, vx2)]
                        if v_crop.size > 0 and (vx2 - vx1) > 40 and (vy2 - vy1) > 30:
                            plate_data = anpr_engine.read_plate(
                                vehicle_crop=v_crop,
                                camera_id=camera_id,
                                track_id=v_det.track_id,
                                timestamp_sec=timestamp_sec
                            )
                            if plate_data:
                                anpr_processed_tracks.add(v_det.track_id)
                                reading = ANPRReading(
                                    camera_id=camera_id,
                                    track_id=plate_data["track_id"],
                                    plate_text=plate_data["plate_text"],
                                    confidence=plate_data["confidence"],
                                    evidence_crop_path=plate_data.get("evidence_crop_path"),
                                    verification_status=plate_data["verification_status"],
                                    timestamp=round(plate_data["timestamp"], 2)
                                )
                                db.add(reading)

                # Render Annotations
                annotated_frame = self.draw_annotations(
                    frame=frame,
                    detections=all_dets,
                    camera_id=camera_id,
                    timestamp_sec=timestamp_sec,
                    lat=lat,
                    lon=lon,
                    speed_kmh=speed
                )

                writer.write(annotated_frame)

            # Persist Vehicle Counts for Stream
            tracker = fleet_tracker.get_tracker(camera_id)
            for v_class, v_cnt in tracker.counts_by_class.items():
                if v_cnt > 0:
                    count_rec = VehicleCountRecord(
                        camera_id=camera_id,
                        vehicle_class=v_class,
                        count=v_cnt,
                        density_level=tracker.get_traffic_density(),
                        time_window_start=datetime.now(),
                        time_window_end=datetime.now()
                    )
                    db.add(count_rec)

            # Update Bus Source telemetry in DB
            result = await db.execute(select(CameraSource).where(CameraSource.bus_id == camera_id))
            source = result.scalar_one_or_none()
            if source:
                source.total_frames_processed += frame_count
                source.total_incidents_detected += incidents_created
                source.current_lat = lat
                source.current_lon = lon
                source.fps = round(fps, 1)
                await db.commit()

        finally:
            cap.release()
            writer.release()

        elapsed_sec = max(time.time() - start_time, 0.001)
        proc_fps = round(frame_count / elapsed_sec, 1)
        tracker = fleet_tracker.get_tracker(camera_id)

        logger.info(
            f"Video processing finished in {elapsed_sec:.2f}s ({proc_fps} FPS). "
            f"Frames: {frame_count}, Incidents: {incidents_created}, Unique Vehicles: {len(tracker.counted_track_ids)}"
        )

        return {
            "status": "completed",
            "camera_id": camera_id,
            "frames_processed": frame_count,
            "total_video_frames": total_video_frames,
            "processing_fps": proc_fps,
            "elapsed_seconds": round(elapsed_sec, 2),
            "incidents_created": incidents_created,
            "annotated_video_path": f"evidence/{output_filename}",
            "unique_vehicles_counted": len(tracker.counted_track_ids),
            "anpr_readings_count": len(anpr_processed_tracks),
            "counts_by_class": dict(tracker.counts_by_class),
            "traffic_density": tracker.get_traffic_density()
        }


video_service = VideoProcessingService()
