import torch
import torch.nn as nn
import torch.nn.functional as F

class SupConLoss(nn.Module):
    """
    Supervised Contrastive Loss (SupCon).
    Based on: Khosla et al. (2020) 'Supervised Contrastive Learning'.
    """
    def __init__(self, temperature: float = 0.07):
        super().__init__()
        self.temperature = temperature

    def forward(self, features: torch.Tensor, labels: torch.Tensor) -> torch.Tensor:
        """
        Args:
            features: (B, D) - normalized embeddings
            labels: (B,) - class labels
        """
        device = features.device
        batch_size = features.shape[0]

        # Normalize features
        features = F.normalize(features, p=2, dim=1)

        # Compute cosine similarity matrix
        similarity_matrix = torch.matmul(features, features.T) # (B, B)

        # Create mask for positive pairs (same label)
        labels = labels.contiguous().view(-1, 1)
        mask = torch.eq(labels, labels.T).float().to(device)

        # Mask out self-similarities
        logits_mask = torch.scatter(
            torch.ones_like(mask),
            1,
            torch.arange(batch_size).view(-1, 1).to(device),
            0
        )
        mask = mask * logits_mask

        # Compute logits
        logits = similarity_matrix / self.temperature

        # For each positive pair, compute the contrastive loss
        # exp(sim(i,j)/T) / sum(exp(sim(i,k)/T))
        exp_logits = torch.exp(logits) * logits_mask
        log_prob = logits - torch.log(exp_logits.sum(1, keepdim=True) + 1e-6)

        # Mean log-prob over positives
        mean_log_prob_pos = (mask * log_prob).sum(1) / (mask.sum(1) + 1e-6)

        loss = -mean_log_prob_pos.mean()
        return loss
