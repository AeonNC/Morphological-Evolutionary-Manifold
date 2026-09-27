import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from typing import Dict, Any, Optional, List
from pathlib import Path
from ..utils.paths import paths
from .logging import ExperimentLogger

class MEMTrainer:
    """
    Advanced Trainer for MEM models supporting multi-task learning,
    SupCon, and reproducibility.
    """
    def __init__(self,
                 model: nn.Module,
                 config: Dict[str, Any],
                 optimizer_cls: type = optim.AdamW,
                 scheduler_cls: type = optim.lr_scheduler.CosineAnnealingLR):
        self.model = model
        self.config = config
        self.device = torch.device(config.get('device', 'cuda') if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)

        self.optimizer = optimizer_cls(self.model.parameters(), lr=config.get('lr0', 1e-4))
        self.scheduler = scheduler_cls(self.optimizer, T_max=config.get('epochs', 100))

        self.logger = ExperimentLogger(config)
        self.scaler = torch.cuda.amp.GradScaler() if self.device.type == 'cuda' else None

    def _compute_multi_task_loss(self, predictions: tuple, targets: Dict[str, torch.Tensor]) -> Tuple[torch.Tensor, Dict[str, float]]:
        """
        Calculates a weighted sum of losses: Disease, Attributes, and SupCon.
        """
        disease_logits, attr_logits, embeddings = predictions

        # 1. Disease Loss (Cross Entropy)
        criterion_ce = nn.CrossEntropyLoss()
        loss_disease = criterion_ce(disease_logits, targets['disease'])

        # 2. Attribute Loss (BCE for multi-label attributes)
        criterion_bce = nn.BCEWithLogitsLoss()
        loss_attr = criterion_bce(attr_logits, targets['attr'])

        # 3. SupCon Loss (Supervised Contrastive)
        # We assume a SupConLoss module is passed or available
        from ..losses.supcon import SupConLoss
        supcon_crit = SupConLoss(temperature=self.config.get('temperature', 0.07)).to(self.device)
        loss_supcon = supcon_crit(embeddings, targets['disease'])

        # Weighting
        w_d = self.config.get('lambda_disease', 1.0)
        w_a = self.config.get('lambda_attr', 0.5)
        w_s = self.config.get('lambda_supcon', 1.0)

        total_loss = (w_d * loss_disease) + (w_a * loss_attr) + (w_s * loss_supcon)

        metrics = {
            "loss_total": total_loss.item(),
            "loss_disease": loss_disease.item(),
            "loss_attr": loss_attr.item(),
            "loss_supcon": loss_supcon.item()
        }

        return total_loss, metrics

    def train_epoch(self, train_loader: DataLoader, targets_key: Dict[str, str]):
        self.model.train()
        total_metrics = {}

        for batch_idx, (images, labels_dict) in enumerate(train_loader):
            images = images.to(self.device)
            # Prepare targets
            targets = {k: labels_dict[v].to(self.device) for k, v in targets_key.items()}

            self.optimizer.zero_grad()

            with torch.cuda.amp.autocast(enabled=self.scaler is not None):
                preds = self.model(images)
                loss, metrics = self._compute_multi_task_loss(preds, targets)

            if self.scaler:
                self.scaler.scale(loss).backward()
                self.scaler.step(self.optimizer)
                self.scaler.update()
            else:
                loss.backward()
                self.optimizer.step()

            # Aggregate metrics
            for k, v in metrics.items():
                total_metrics[k] = total_metrics.get(k, 0) + v

        self.scheduler.step()

        # Average metrics
        avg_metrics = {k: v / len(train_loader) for k, v in total_metrics.items()}
        return avg_metrics

    def validate(self, val_loader: DataLoader, targets_key: Dict[str, str]):
        self.model.eval()
        total_metrics = {}

        with torch.no_grad():
            for images, labels_dict in val_loader:
                images = images.to(self.device)
                targets = {k: labels_dict[v].to(self.device) for k, v in targets_key.items()}

                preds = self.model(images)
                loss, metrics = self._compute_multi_task_loss(preds, targets)

                for k, v in metrics.items():
                    total_metrics[k] = total_metrics.get(k, 0) + v

        return {k: v / len(val_loader) for k, v in total_metrics.items()}
