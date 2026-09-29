import pandas as pd
from pathlib import Path
from typing import List, Dict, Any

class MixtureBuilder:
    """
    Creates simulated MRD-style rare-cell mixtures for anomaly detection.
    """
    def __init__(self, manifest_path: Path):
        self.df = pd.read_parquet(manifest_path)

    def create_prevalence_suite(self, prevalences: List[float]) -> Dict[float, List[List[Dict]]]:
        """
        Builds mixtures for multiple prevalence levels.
        Each mixture is a 'bag' of cells.
        """
        suite = {}
        for p in prevalences:
            suite[p] = self._generate_mixture(p)
        return suite

    def _generate_mixture(self, prevalence: float) -> List[List[Dict]]:
        """
        Creates a set of mixture bags.
        """
        # 1. Separate Normal and Abnormal based on labels
        normal_cells = self.df[self.df['disease_label'] == 'normal'].to_dict('records')
        abnormal_cells = self.df[self.df['disease_label'] != 'normal'].to_dict('records')

        bags = []
        for _ in range(10): # Generate 10 bags per level
            bag_size = 1000
            n_abnormal = int(bag_size * prevalence)
            n_normal = bag_size - n_abnormal

            # Sample without replacement
            import random
            selected_abnormal = random.sample(abnormal_cells, min(n_abnormal, len(abnormal_cells)))
            selected_normal = random.sample(normal_cells, min(n_normal, len(normal_cells)))

            bag = selected_abnormal + selected_normal
            random.shuffle(bag)
            bags.append(bag)

        return bags
