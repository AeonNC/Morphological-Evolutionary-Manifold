import torch
import torch.nn as nn
from torch.cuda.amp import GradScaler, autocast
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR
import logging

class MEMTrainer:
    """
    Safety-first trainer for MEM models.
    """
    def __init__(self, model, train_loader, val_loader, optimizer_config: dict):
        self.model = model
        self.train_loader = train_loader
        self.val_loader = val_loader

        self.optimizer = AdamW(model.parameters(), **optimizer_config)
        self.scheduler = CosineAnnealingLR(self.optimizer, T_max=10) # Simplified
        self.scaler = GradScaler()

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

    def train_epoch(self, epoch: int):
        self.model.train()
        total_loss = 0

        for batch_idx, (data, target) in enumerate(self.train_loader):
            data, target = data.to(self.device), target.to(self.device)

            self.optimizer.zero_grad()

            with autocast():
                output = self.model(data)
                # In a real scenario, output would be (global, local)
                # We use a mock loss here for the skeleton
                loss = torch.tensor(0.1, requires_grad=True).to(self.device)

            self.scaler.scale(loss).backward()

            # Gradient clipping to prevent exploding gradients
            self.scaler.unscale_(self.optimizer)
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)

            self.scaler.step(self.optimizer)
            self.scaler.update()

            # NaN/Inf check
            if torch.isnan(loss) or torch.isinf(loss):
                logging.error(f"NaN/Inf loss detected at epoch {epoch}, batch {batch_idx}")
                return None

            total_loss += loss.item()

        self.scheduler.step()
        return total_loss / len(self.train_loader)

    def validate(self):
        self.model.eval()
        # Simplified validation logic
        return {"val_loss": 0.1}
