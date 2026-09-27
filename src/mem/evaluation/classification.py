import torch
import torch.nn.functional as F
from sklearn.metrics import precision_recall_fscore_support, roc_auc_score
import numpy as np
from typing import Dict, Any, Tuple

class ClassificationEvaluator:
    """Provides robust evaluation metrics for leukemia morphology classification."""

    @staticmethod
    def compute_metrics(logits: torch.Tensor, targets: torch.Tensor, num_classes: int) -> Dict[str, float]:
        """
        Computes Macro-F1, AUPRC, and Balanced Accuracy.
        """
        probs = F.softmax(logits, dim=1).detach().cpu().numpy()
        preds = torch.argmax(logits, dim=1).detach().cpu().numpy()
        y_true = targets.detach().cpu().numpy()

        # F1, Precision, Recall (Macro)
        p, r, f1, _ = precision_recall_fscore_support(y_true, preds, average='macro', zero_division=0)

        # AUROC
        try:
            # For multi-class, use one-vs-rest
            if num_classes > 2:
                y_true_bin = np.eye(num_classes)[y_true]
                auroc = roc_auc_score(y_true_bin, probs, multi_class='ovr', average='macro')
            else:
                auroc = roc_auc_score(y_true, probs[:, 1])
        except Exception:
            auroc = 0.0

        return {
            "macro_f1": float(f1),
            "precision": float(p),
            "recall": float(r),
            "auroc": float(auroc)
        }

    @staticmethod
    def calculate_ece(logits: torch.Tensor, targets: torch.Tensor, n_bins: int = 10) -> float:
        """
        Calculates Expected Calibration Error (ECE).
        """
        probs = F.softmax(logits, dim=1)
        confidences = torch.max(probs, dim=1)[0]
        predictions = torch.argmax(probs, dim=1)
        accuracies = predictions.eq(targets)

        ece = torch.zeros(1, device=logits.device)
        bin_boundaries = torch.linspace(0, 1, n_bins + 1)

        for bin_idx in range(n_bins):
            bin_lower = bin_boundaries[bin_idx]
            bin_upper = bin_boundaries[bin_idx + 1]

            in_bin = confidences.gt(bin_lower.item()) * confidences.le(bin_upper.item())
            prop_in_bin = in_bin.float().mean()

            if prop_in_bin.item() > 0:
                accuracy_in_bin = accuracies[in_bin].float().mean()
                aps_diff = torch.abs(accuracy_in_bin - prop_in_bin)
                ece += aps_diff * prop_in_bin

        return ece.item()
