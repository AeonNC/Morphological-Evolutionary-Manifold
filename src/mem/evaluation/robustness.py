import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional
from sklearn.metrics import f1_score, precision_score, recall_score

def evaluate_robustness(y_true: np.ndarray, y_pred: np.ndarray, domain_id: str) -> Dict[str, Any]:
    """
    Evaluates model performance on a specific domain (e.g., a different dataset).
    """
    return {
        "domain": domain_id,
        "f1": f1_score(y_true, y_pred, average='weighted'),
        "precision": precision_score(y_true, y_pred, average='weighted'),
        "recall": recall_score(y_true, y_pred, average='weighted'),
    }

def cross_domain_analysis(results: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Aggregates results across multiple domains to identify the weakest link.
    """
    return pd.DataFrame(results)

def analyze_stain_impact(results_by_stain: Dict[str, Dict[str, Any]]) -> pd.DataFrame:
    """
    Compares performance across different stain normalization methods.
    """
    return pd.DataFrame(results_by_stain).T
