import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional
from ..utils.paths import paths

class PatchExtractor:
    """Extracts standardized cell patches from full-field images using bounding boxes."""

    def __init__(self, target_size: int = 256, padding_ratio: float = 0.2):
        self.target_size = target_size
        self.padding_ratio = padding_ratio

    def extract(self, image: np.ndarray, box: List[float],
                 record_id: str, output_dir: Path) -> Optional[str]:
        """
        Extracts a square patch from an image given a bounding box [x1, y1, x2, y2].
        Applies reflected padding and resizes to target_size.
        """
        x1, y1, x2, y2 = map(int, box)
        h, w = image.shape[:2]

        # Calculate center and required size for square crop
        box_w = x2 - x1
        box_h = y2 - y1
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2

        # Calculate crop size with padding
        max_dim = max(box_w, box_h) * (1 + self.padding_ratio)

        # Determine crop boundaries
        start_x = int(center_x - max_dim / 2)
        start_y = int(center_y - max_dim / 2)
        end_x = int(start_x + max_dim)
        end_y = int(start_y + max_dim)

        # Handle borders using reflected padding
        # Calculate necessary padding for each side
        pad_left = max(0, -start_x)
        pad_top = max(0, -start_y)
        pad_right = max(0, start_x + max_dim - w) # Wait, should use end_x
        pad_right = max(0, end_x - w)
        pad_bottom = max(0, end_y - h)

        # Crop the available region
        crop_x1 = max(0, start_x)
        crop_y1 = max(0, start_y)
        crop_x2 = min(w, end_x)
        crop_y2 = min(h, end_y)

        crop = image[crop_y1:crop_y2, crop_x1:crop_x2]

        # Apply reflected padding
        padded = cv2.copyMakeBorder(
            crop,
            pad_top, pad_bottom, pad_left, pad_right,
            borderType=cv2.BORDER_REFLECT
        )

        # Final resize to target size
        final_patch = cv2.resize(padded, (self.target_size, self.target_size),
                                interpolation=cv2.INTER_AREA)

        # Save patch
        patch_filename = f"{record_id}.png"
        patch_path = output_dir / patch_filename
        cv2.imwrite(str(patch_path), final_patch)

        return str(patch_path)
