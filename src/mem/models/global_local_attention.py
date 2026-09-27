import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Tuple

class GlobalLocalAttention(nn.Module):
    """
    Implements the Gated Global-Local Attention fusion mechanism.

    Inputs:
        global_feat: (B, C) - typically the CLS token
        local_feats: (B, N, C) - typically the patch tokens
    """
    def __init__(self, embed_dim: int):
        super().__init__()
        self.embed_dim = embed_dim

        # Local attention pooling: Learns which patches are most relevant to morphology
        self.local_pool = nn.Sequential(
            nn.Linear(embed_dim, 1),
            nn.Softmax(dim=1)
        )

        # Gating mechanism to balance global vs local signal
        self.gate = nn.Sequential(
            nn.Linear(embed_dim * 2, 1),
            nn.Sigmoid()
        )

        # Residual projection to maintain dimensionality
        self.proj = nn.Linear(embed_dim, embed_dim)

    def forward(self, global_feat: torch.Tensor, local_feats: torch.Tensor) -> torch.Tensor:
        B, N, C = local_feats.shape

        # 1. Local Branch: Weighted average of patches
        weights = self.local_pool(local_feats) # (B, N, 1)
        local_feat = torch.sum(weights * local_feats, dim=1) # (B, C)

        # 2. Gating: Decide how much to trust global vs local
        gate_input = torch.cat([global_feat, local_feat], dim=-1) # (B, 2C)
        g = self.gate(gate_input) # (B, 1)

        # 3. Fusion: Gated linear combination
        fused = g * global_feat + (1 - g) * local_feat

        # 4. Residual Connection
        return self.proj(fused) + global_feat
