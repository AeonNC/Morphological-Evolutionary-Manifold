import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Any, List, Tuple
import numpy as np
from .classification import ClassificationEvaluator

class DomainRobustnessEvaluator:
    """
    Systematically evaluates model performance across different
    stain normalization methods and dataset shifts.
    """
    def __init__(self, model: nn.Module, evaluator: ClassificationEvaluator):
        self.model = model
        self.evaluator = evaluator

    def evaluate_cross_domain(self,
                              train_loader,
                              test_loaders: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates the model on multiple external test sets.
        test_loaders: {'ALL-IDB': loader, 'Mixed-HPF': loader, ...}
        """
        self.model.eval()
        results = {}

        with torch.no_grad():
            for domain_name, loader in test_loaders.items():
                all_logits = []
                all_targets = []

                for images, labels_dict in loader:
                    # Assume labels_dict contains 'disease'
                    logits, _, _ = self.model(images)
                    all_logits.append(logits)
                    all_targets.append(labels_dict['disease'])

                logits_tensor = torch.cat(all_logits, dim=0)
                targets_tensor = torch.cat(all_targets, dim=0)

                # Use the classification evaluator
                metrics = self.evaluator.compute_metrics(
                    logits_tensor,
                    targets_tensor,
                    num_classes=2 # Binary: AML/ALL vs Control
                )
                results[domain_name] = metrics

        return results

    def evaluate_stain_impact(self,
                              test_loader: Any,
                              normalization_funcs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Tests how different normalization methods affect the same test set.
        normalization_funcs: {'raw': func, 'macenko': func, 'reinhard': func}
        """
        self.model.eval()
        stain_results = {}

        for method, func in normalization_fonts.items():
            all_logits = []
            all_targets = []

            with torch.no_grad():
                for images, labels_dict in test_loader:
                    # Apply normalization to images
                    norm_images = torch.stack([func(img) for img in images])
                    logits, _, _ = self.model(norm_images)

                    all_logits.append(logits)
                    all_targets.append(labels_dict['disease'])

            logits_tensor = torch.cat(all_logits, dim=0)
            targets_tensor = torch.cat(all_targets, dim=0)
            stain_results[method] = self.evaluator.compute_metrics(logits_tensor, targets_tensor, 2)

        return stain_results
