import numpy as np
import torch
from pathlib import Path
from typing import List, Dict, Any, Tuple
from ..utils.paths import paths

class MixtureGenerator:
    """
    Creates controlled rare-cell mixtures for MRD-inspired benchmarks.
    """
    def __init__(self, manifest_path: str):
        import pandas as pd
        self.df = pd.read_parquet(manifest_path)

    def create_mixture(self,
                       normal_dataset: str,
                       abnormal_dataset: str,
                       prevalence: float,
                       bag_size: int = 1000,
                       seed: int = 42) -> Dict[str, Any]:
        """
        Generates a synthetic bag of cells with a specific prevalence of abnormal cells.
        """
        np.random.seed(seed)

        # 1. Filter sources
        normals = self.df[self.df['dataset_name'] == normal_dataset]
        abnormals = self.df[self.df['dataset_name'] == abnormal_dataset]

        # 2. Determine counts
        n_abnormal = int(bag_size * prevalence)
        n_normal = bag_size - n_abnormal

        # 3. Sample
        norm_samples = normals.sample(n=min(len(normals), n_normal))
        abnorm_samples = abnormals.sample(n=min(len(abnormals), n_abnormal))

        # Combine
        mixture_df = pd.concat([norm_samples, abnorm_samples])

        return {
            "recipe_id": f"mix_{prevalence}_{seed}",
            "prevalence": prevalence,
            "bag_size": len(mixture_df),
            "abnormal_count": len(abnorm_samples),
            "records": mixture_df['record_id'].tolist()
        }
