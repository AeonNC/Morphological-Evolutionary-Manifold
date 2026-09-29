import torch
import torch.nn as nn
import torch.nn.functional as F

class SupConLoss(nn.Module):
    """
    Supervised Contrastive Loss (SupCon).
    Encourages samples of the same class to be close and different classes to be far.
    """
    def __init__(self, temperature: float = 0.07):
        super().__init__()
        self.temperature = temperature

    def forward(self, features: torch.Tensor, labels: torch.Tensor):
        """
        features: [B, D]
        labels: [B]
        """
        # L2 Normalize features
        features = F.normalize(features, p=2, dim=1)

        batch_size = features.shape[0]
        labels = labels.contiguous().view(-1, 1)

        # Mask for positives (same class)
        mask = torch.eq(labels, labels.T).float().to(features.device)
        # Remove self-contrast
        mask.fill_diagonal_(0)

        # Compute cosine similarity
        logits = torch.matmul(features, features.T) / self.temperature

        # For each positive pair, compute the contrastive loss
        exp_logits = torch.exp(logits)

        # Sum of exp(logits) for all negatives (and positives)
        denom = exp_logits.sum(1, keepdim=True)

        # Masked contrastive loss
        # log( exp(pos) / sum(exp(all)) )
        pos_logits = (exp_logits * mask).sum(1, keepdim=True) / (mask.sum(1, keepdim=True) + 1e-6)

        loss = -torch.log(pos_logits / denom).mean()

        return loss
