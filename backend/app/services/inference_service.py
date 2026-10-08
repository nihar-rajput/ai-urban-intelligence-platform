import os
from typing import List, Dict, Any, Optional
import cv2
import numpy as np
import torch
from ultralytics import YOLO

from backend.app.core.config import settings
from backend.app.core.logging import logger


class DetectionResult:
    def __init__(
        self,
        box: List[int],
        class_name: str,
        confidence: float,
        detector_source: str,
        track_id: Optional[int] = None
    ):
        self.box = box  # [x1, y1, x2, y2]
        self.class_name = class_name
        self.confidence = confidence
        self.detector_source = detector_source
        self.track_id = track_id

    def to_dict(self) -> Dict[str, Any]:
        return {
            "box": self.box,
            "class_name": self.class_name,
            "confidence": round(self.confidence, 4),
            "detector_source": self.detector_source,
            "track_id": self.track_id
        }


class InferenceEngine:
    """
    Centralized Inference Engine managing vehicle/pedestrian detection and road defect detection.
    Enforces GPU acceleration (RTX 4050 / CUDA) with automatic CPU fallback.
    """

    def __init__(self):
        self.device = settings.DEVICE
        self.vehicle_model: Optional[YOLO] = None
        self.defect_model: Optional[YOLO] = None
        self._init_models()

    def _init_models(self):
        # 1. Vehicle & Pedestrian Detector (YOLOv8n)
        try:
            logger.info(f"Loading YOLO vehicle model on device '{self.device}'...")
            self.vehicle_model = YOLO("yolov8n.pt")
            logger.info(f"Vehicle detector initialized successfully on {self.device}.")
        except Exception as e:
            logger.error(f"Failed to initialize vehicle detector: {e}")
            self.vehicle_model = None

        # 2. Road Defect Model (Custom fine-tuned weights)
        if os.path.exists(settings.YOLO_ROAD_DEFECT_MODEL):
            try:
                logger.info(f"Loading fine-tuned Road Defect model from {settings.YOLO_ROAD_DEFECT_MODEL}...")
                self.defect_model = YOLO(settings.YOLO_ROAD_DEFECT_MODEL)
                logger.info("Road Defect model loaded successfully.")
            except Exception as e:
                logger.warning(f"Could not load custom defect model: {e}")
                self.defect_model = None
        else:
            logger.info(f"Road Defect model weights '{settings.YOLO_ROAD_DEFECT_MODEL}' not found. Defect pipeline in preview/dataset collection mode.")
            self.defect_model = None

    def detect_vehicles(self, frame: np.ndarray, conf_threshold: float = 0.30) -> List[DetectionResult]:
        """Detect supported vehicle categories and pedestrians using YOLOv8."""
        if self.vehicle_model is None:
            return []

        results = self.vehicle_model.predict(
            frame,
            conf=conf_threshold,
            device=self.device,
            verbose=False
        )

        detections: List[DetectionResult] = []
        # Target COCO classes: 0: person, 1: bicycle, 2: car, 3: motorcycle, 5: bus, 7: truck
        target_classes = {0: "person", 1: "bicycle", 2: "car", 3: "motorcycle", 5: "bus", 7: "truck"}

        for r in results:
            boxes = r.boxes
            for b in boxes:
                cls_id = int(b.cls[0].item())
                if cls_id in target_classes:
                    xyxy = b.xyxy[0].cpu().numpy().astype(int).tolist()
                    conf = float(b.conf[0].item())
                    detections.append(
                        DetectionResult(
                            box=xyxy,
                            class_name=target_classes[cls_id],
                            confidence=conf,
                            detector_source="yolo_vehicle_coco"
                        )
                    )
        return detections

    def detect_road_defects(self, frame: np.ndarray, conf_threshold: float = 0.35) -> List[DetectionResult]:
        """
        Detect potholes, surface cracks, or hazard depressions.
        If a fine-tuned model exists, runs neural inference.
        Otherwise, runs an explainable road-region optical depression analyzer (clearly labeled as HEURISTIC_PREVIEW).
        """
        detections: List[DetectionResult] = []

        # Case A: Fine-tuned neural network is available
        if self.defect_model is not None:
            results = self.defect_model.predict(
                frame,
                conf=conf_threshold,
                device=self.device,
                verbose=False
            )
            for r in results:
                for b in r.boxes:
                    cls_id = int(b.cls[0].item())
                    cls_name = self.defect_model.names.get(cls_id, f"defect_{cls_id}")
                    xyxy = b.xyxy[0].cpu().numpy().astype(int).tolist()
                    conf = float(b.conf[0].item())
                    detections.append(
                        DetectionResult(
                            box=xyxy,
                            class_name=cls_name,
                            confidence=conf,
                            detector_source="road_defect_model"
                        )
                    )
            return detections

        # Case B: Heuristic Optical Road Hazard Detector (for un-trained demo/preview)
        # Inspects the lower road perspective region for dark road depressions with sharp gradients
        h, w = frame.shape[:2]
        road_roi_y_start = int(h * 0.50)
        roi = frame[road_roi_y_start:, :]

        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (7, 7), 0)

        # Threshold for deeply dark road depressions / pothole shapes
        _, thresh = cv2.threshold(blurred, 35, 255, cv2.THRESH_BINARY_INV)

        # Morphological open to remove noise
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        opened = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

        contours, _ = cv2.findContours(opened, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            area = cv2.contourArea(cnt)
            # Filter contours by realistic pothole area
            if 300 < area < 15000:
                x, y, cw, ch = cv2.boundingRect(cnt)
                aspect_ratio = float(cw) / max(ch, 1)
                # Potholes viewed from perspective road cameras have horizontal aspect ratio 1.1 - 3.5
                if 0.8 <= aspect_ratio <= 4.0:
                    real_y1 = road_roi_y_start + y
                    real_y2 = real_y1 + ch
                    real_x1 = x
                    real_x2 = x + cw
                    detections.append(
                        DetectionResult(
                            box=[real_x1, real_y1, real_x2, real_y2],
                            class_name="POTHOLE",
                            confidence=0.72,
                            detector_source="HEURISTIC_PREVIEW"
                        )
                    )

        return detections


inference_engine = InferenceEngine()
