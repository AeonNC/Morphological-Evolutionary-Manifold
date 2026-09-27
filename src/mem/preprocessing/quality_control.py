import cv2
import numpy as np
from typing import Dict, Any, Tuple
from pathlib import Path

class QualityControl:
    """Performs image quality assessment for blood smear patches."""

    @staticmethod
    def calculate_blur_score(image: np.ndarray) -> float:
        """
        Calculate the Variance of Laplacian to estimate focus.
        Higher value = sharper image.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return cv2.Laplacian(gray, cv2.CV_64F).var()

    @staticmethod
    def calculate_brightness_contrast(image: np.ndarray) -> Tuple[float, float]:
        """
        Returns mean brightness and standard deviation (contrast).
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return np.mean(gray), np.std(gray)

    @staticmethod
    def calculate_saturation(image: np.ndarray) -> float:
        """
        Calculate mean saturation using HSV color space.
        """
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        return np.mean(hsv[:, :, 1])

    def evaluate_patch(self, image: np.ndarray) -> Dict[str, float]:
        """Perform full QC on a single patch."""
        brightness, contrast = self.calculate_brightness_contrast(image)
        return {
            "quality_blur_score": self.calculate_blur_score(image),
            "quality_brightness_score": brightness,
            "quality_contrast_score": contrast,
            "quality_saturation_score": self.calculate_saturation(image)
        }
