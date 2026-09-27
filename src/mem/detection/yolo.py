from ultralytics import YOLO
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional
import torch
from ..utils.paths import paths

class YOLODetector:
    """Wrapper for Ultralytics YOLO to handle blood cell localization."""

    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            import yaml
            self.config = yaml.safe_load(f)

        self.model_name = self.config.get('model_name', 'yolo11n.pt')
        self.model = YOLO(self.model_name)

    def train(self, data_yaml: str, output_dir: Optional[str] = None):
        """Train the detector on the specified dataset."""
        out_dir = output_dir or paths.get_output_path("runs/detect/train")

        results = self.model.train(
            data=data_yaml,
            epochs=self.config.get('epochs', 100),
            imgsz=self.config.get('img_size', 640),
            batch=self.config.get('batch', -1),
            optimizer=self.config.get('optimizer', 'AdamW'),
            lr0=self.config.get('lr0', 0.001),
            lrf=self.config.get('lrf', 0.01),
            cos_lr=self.config.get('cos_lr', True),
            warmup_epochs=self.config.get('warmup_epochs', 3),
            patience=self.config.get('patience', 20),
            seed=self.config.get('seed', 42),
            augment=self.config.get('augment', True),
            mosaic=self.config.get('mosaic', 0.5),
            mixup=self.config.get('mixup', 0.0),
            close_mosaic=self.config.get('close_mosaic', 10),
            project=str(out_dir),
            name="exp"
        )
        return results

    def predict(self, image_path: str, conf_threshold: float = 0.25) -> List[Dict[str, Any]]:
        """
        Predict bounding boxes for a single image.
        Returns a list of dicts: [{'class': int, 'box': [x1, y1, x2, y2], 'conf': float}]
        """
        results = self.model.predict(source=image_path, conf=conf_threshold, verbose=False)
        result = results[0]

        detections = []
        boxes = result.boxes
        for box in boxes:
            detections.append({
                'class': int(box.cls),
                'box': box.xyxy[0].tolist(),
                'conf': float(box.conf)
            })
        return detections

    def evaluate(self, data_yaml: str) -> Dict[str, float]:
        """Run validation and return key metrics."""
        metrics = self.model.val(data=data_yaml)
        return {
            "mAP50": metrics.box.map50,
            "mAP50-95": metrics.box.map,
            "precision": metrics.box.mp,
            "recall": metrics.box.mr,
            "f1": metrics.box.f1.mean()
        }
