import numpy as np
from typing import List, Dict, Any, Tuple
from .persistence import PersistenceAnalyzer
from .graph_analysis import GraphAnalyzer # Assuming this exists or will be built

class MCDSCalculator:
    """
    Calculates the Morphological Clonal Diversity Score (MCDS).
    MCDS = w1*z(H0_entropy) + w2*z(H1_entropy) + w3*z(total_pers) + ...
    """
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.weights = weights or {
            "h0_entropy": 0.2,
            "h1_entropy": 0.2,
            "total_persistence": 0.2,
            "graph_modularity": 0.2,
            "dispersion": 0.2
        }
        self.analyzer = PersistenceAnalyzer()

    def compute_score(self, embeddings: np.ndarray,
                      training_stats: Dict[str, Dict[str, float]]) -> float:
        """
        Computes MCDS for a single bag of cells.
        training_stats: { "h0_entropy": {"mean": ..., "std": ...}, ... }
        """
        # 1. Topological Features
        b0, d0 = self.analyzer.compute_persistence(embeddings, dimension=0)
        h0_ent = self.analyzer.compute_persistence_entropy(b0, d0)

        b1, d1 = self.analyzer.compute_persistence(embeddings, dimension=1)
        h1_ent = self.analyzer.compute_persistence_entropy(b1, d1)

        total_pers = np.sum(d0 - b0) + np.sum(d1 - b1)

        # 2. Geometric Features
        dispersion = np.std(embeddings)

        # Mock graph modularity (will be replaced by GraphAnalyzer)
        modularity = 0.5

        # 3. Z-Normalization and Weighting
        components = {
            "h0_entropy": h0_ent,
            "h1_entropy": h1_ent,
            "total_persistence": total_pers,
            "graph_modularity": modularity,
            "dispersion": dispersion
        }

        score = 0.0
        for key, value in components.items():
            stats = training_stats.get(key, {"mean": 0, "std": 1})
            z = (value - stats["mean"]) / (stats["std"] + 1e-6)
            score += self.weights.get(key, 0) * z

        return score
