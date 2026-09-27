import torch
import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Any
from PIL import Image
from ..utils.paths import paths

class ErrorAnalyzer:
    """Generates visual montages of model failures for clinical error analysis."""

    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or paths.get_output_path("figures/error_analysis")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_confusion_montage(self,
                                   model: nn.Module,
                                   loader: Any,
                                   class_a: int,
                                   class_b: int,
                                   n_images: int = 16):
        """
        Finds images where model predicted class_a but ground truth was class_b.
        Saves a montage of these 'hard negatives'.
        """
        model.eval()
        failures = []

        with torch.no_grad():
            for images, labels_dict in loader:
                logits, _, _ = model(images)
                preds = torch.argmax(logits, dim=1)
                targets = labels_dict['disease']

                # Mask for specific confusion: Pred=A and Target=B
                mask = (preds == class_a) & (targets == class_b)

                for i in range(len(mask)):
                    if mask[i] and len(failures) < n_images:
                        # Store image and its metadata
                        failures.append(images[i].cpu().numpy())

        if not failures:
            print("No failures found for the specified classes.")
            return

        # Create montage
        grid_size = int(np.ceil(np.sqrt(len(failures))))
        montage = np.ones((grid_size * 256, grid_size * 256, 3), dtype=np.uint8) * 255

        for idx, img in enumerate(failures):
            # Denormalize and convert to uint8
            img = (img.transpose(1, 2, 0) * 0.5 + 0.5) * 255.0
            img = np.clip(img, 0, 255).astype(np.uint8)

            row = idx // grid_size
            col = idx % grid_size
            montage[row*256:(row+1)*256, col*256:(col+1)*256] = img

        save_path = self.output_dir / f"confusion_{class_a}_vs_{class_b}.jpg"
        cv2.imwrite(str(save_path), cv2.cvtColor(montage, cv2.COLOR_RGB2BGR))
        print(f"Confusion montage saved to {save_path}")
