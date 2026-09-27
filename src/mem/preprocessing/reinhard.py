import cv2
import numpy as np
from typing import Optional

class ReinhardNormalizer:
    """
    Implements Reinhard stain normalization.
    Based on: Reinhard et al. (2008).
    """

    def __init__(self, reference_image: Optional[np.ndarray] = None):
        self.ref_mean = None
        self.ref_std = None
        if reference_image is not None:
            self.fit(reference_image)

    def fit(self, reference_image: np.ndarray):
        """Compute mean and std of the reference image in Lab space."""
        lab = cv2.cvtColor(reference_image, cv2.COLOR_BGR2Lab)
        self.ref_mean = np.mean(lab, axis=(0, 1))
        self.ref_std = np.std(lab, axis=(0, 1))

    def normalize(self, image: np.ndarray) -> np.ndarray:
        """Normalize target image to match reference Lab statistics."""
        if self.ref_mean is None or self.ref_std is None:
            raise ValueError("Normalizer must be fitted with a reference image first.")

        lab = cv2.cvtColor(image, cv2.COLOR_BGR2Lab).astype(np.float32)

        # Subtract mean and scale by std
        curr_mean = np.mean(lab, axis=(0, 1))
        curr_std = np.std(lab, axis=(0, 1))

        # Avoid division by zero
        curr_std[curr_std == 0] = 1.0

        normalized = (lab - curr_mean) * (self.ref_std / curr_std) + self.ref_mean

        # Clip to valid Lab range
        # L: 0-100, a: -127 to 127, b: -127 to 127
        normalized[:, :, 0] = np.clip(normalized[:, :, 0], 0, 100)
        normalized[:, :, 1] = np.clip(normalized[:, :, 1], -127, 127)
        normalized[:, :, 2] = np.clip(normalized[:, :, 2], -127, 127)

        res = cv2.cvtColor(normalized.astype(np.uint8), cv2.COLOR_Lab2BGR)
        return res
