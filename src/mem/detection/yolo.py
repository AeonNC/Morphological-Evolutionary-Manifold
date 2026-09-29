import torch
from ultralytics import YOLO
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd

class MEMDetector:
    """
    Wrapper for Ultralytics YOLO for blood cell localization.
    """
    def __init__(self, model_path: Optional[str] = None, model_variant: str = "yolo11n.pt"):
        self.model_variant = model_variant
        if model_path:
            self.model = YOLO(model_path)
        else:
            # Default to pretrained weights from ultralytics
            self.model = YOLO(model_variant)

    def detect(self, image_path: Path, conf_threshold: float = 0.25) -> List[Dict[str, Any]]:
        """
        Detects cells in an image and returns a list of bounding boxes.
        """
        results = self.model.predict(source=str(image_path), conf=conf_threshold, verbose=False)

        detections = []
        for r in results:
            boxes = r.boxes
            for box in boxes:
                # Convert to xyxy format
                xyxy = box.xyxy[0].cpu().numpy().tolist()
                cls = int(box.cls[0])
                conf = float(box.conf[0])

                detections.append({
                    "bbox": xyxy,
                    "class": cls,
                    "confidence": conf,
                    "class_name": self.model.names[cls]
                })

        return detections

    def save_model(self, path: Path):
        self.model.save(path)

    def load_model(self, path: Path):
        self.model = YOLO(path)
