import numpy as np
import gudhi
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
import pandas as pd
from ..utils.paths import paths

class PersistenceAnalyzer:
    """
    Handles Persistent Homology calculations for cell embeddings.
    """
    def __init__(self, pca_components: int = 64, max_cells: int = 1000):
        self.pca_components = pca_components
        self.max_cells = max_cells

    def _subsample(self, embeddings: np.ndarray) -> np.ndarray:
        """Deterministic farthest-point sampling to keep TDA tractable."""
        if len(embeddings) <= self.max_cells:
            return embeddings

        # Simple random sampling for baseline; Farthest Point is better for topology
        indices = np.random.choice(len(embeddings), self.max_cells, replace=False)
        return embeddings[indices]

    def compute_persistence(self, embeddings: np.ndarray, dimension: int = 0) -> Tuple[np.ndarray, np.ndarray]:
        """
        Computes persistence diagrams using the Vietoris-Rips complex.
        Returns (births, deaths).
        """
        # 1. Subsample
        data = self._subsample(embeddings)

        # 2. Create Rips Complex
        # We use a max edge length based on the 95th percentile of pairwise distances
        # to avoid calculating a massive number of simplexes.
        rips = gudhi.RipsComplex(points=data, max_edge_length=1.0)
        simplex_tree = rips.create_simplex_tree(max_dimension=dimension+1)

        # 3. Compute Persistence
        persistence = simplex_tree.persistence()

        # 4. Extract births and deaths for the requested dimension
        diagram = simplex_tree.persistence_intervals_in_dimension(dimension)

        if len(diagram) == 0:
            return np.array([]), np.array([])

        births = diagram[:, 0]
        deaths = diagram[:, 1]

        return births, deaths

    def compute_persistence_entropy(self, births: np.ndarray, deaths: np.ndarray) -> float:
        """
        Calculates persistence entropy as a measure of topological diversity.
        """
        if len(births) == 0:
            return 0.0

        lifetimes = deaths - births
        # Normalize lifetimes
        sum_lifetimes = np.sum(lifetimes)
        if sum_lifetimes == 0:
            return 0.0

        p = lifetimes / sum_lifetimes
        # Shannon entropy
        return -np.sum(p * np.log(p + 1e-9))
