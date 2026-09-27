import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import List, Dict, Any, Tuple
from .mixtures import MixtureGenerator

class DeepSVDD(nn.Module):
    """
    Deep SVDD for one-class anomaly detection.
    Learns to map 'normal' cells into a minimum-volume hypersphere.
    """
    def __init__(self, input_dim: int):
        super().__init__()
        # Simple projection head to avoid collapse
        self.net = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 64)
        )
        self.center = None

    def set_center(self, center: torch.Tensor):
        """Initialize the hypersphere center from training data."""
        self.center = center

    def forward(self, x):
        return self.net(x)

    def compute_anomaly_score(self, x: torch.Tensor) -> torch.Tensor:
        """
        The anomaly score is the squared distance to the center.
        """
        if self.center is None:
            raise ValueError("Center must be initialized before scoring.")

        embeddings = self.forward(x)
        dist = torch.sum((embeddings - self.center)**2, dim=1)
        return dist

class AnomalyEvaluator:
    """
    Evaluates rare-cell detection performance.
    """
    def __init__(self, model: DeepSVDD):
        self.model = model

    def evaluate_mixture(self, embeddings: torch.Tensor, labels: torch.Tensor):
        """
        Computes AUPRC and Sensitivity at fixed FPR.
        """
        scores = self.model.compute_anomaly_score(embeddings)

        # Use sklearn for metrics
        from sklearn.metrics import precision_recall_curve, auc, roc_curve

        precision, recall, _ = precision_recall_curve(labels, scores)
        auprc = auc(recall, precision)

        # Sensitivity at 1% FPR
        fpr, tpr, _ = roc_curve(labels, scores)
        idx = np.argmin(np.abs(fpr - 0.01))
        sens_at_1pct_fpr = tpr[idx]

        return {
            "auprc": float(auprc),
            "sensitivity_1pct_fpr": float(sens_at_1pct_fpr)
        }
