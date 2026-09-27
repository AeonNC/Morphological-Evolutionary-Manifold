import torch
import torch.nn as nn
from .backbones import ViTBackbone
from .global_local_attention import GlobalLocalAttention

class MEMViT(nn.Module):
    """
    The core MEM Morphology Manifold model.
    Combines ViT, Global-Local Attention, and multi-task heads.
    """
    def __init__(self,
                 model_name: str = 'vit_small_patch16_224',
                 num_classes_disease: int = 2,
                 num_attrs: int = 11,
                 pretrained: bool = True):
        super().__init__()

        # 1. Representation Backbone
        self.backbone = ViTBackbone(model_name, pretrained=pretrained)
        self.embed_dim = self.backbone.embed_dim

        # 2. Morphology-Aware Attention (GLA)
        self.gla = GlobalLocalAttention(self.embed_dim)

        # 3. Task-Specific Heads
        # We use separate projection heads for different tasks to avoid interference
        self.disease_head = nn.Sequential(
            nn.Linear(self.embed_dim, 256),
            nn.ReLU(),
            nn.Linear(256, num_classes_disease)
        )

        self.attr_head = nn.Sequential(
            nn.Linear(self.embed_dim, 256),
            nn.ReLU(),
            nn.Linear(256, num_attrs)
        )

        # Projection head for Contrastive Learning (SupCon)
        # As per contrastive learning papers, the projection head is dropped during inference
        self.proj_head = nn.Sequential(
            nn.Linear(self.embed_dim, self.embed_dim),
            nn.ReLU(),
            nn.Linear(self.embed_dim, 128)
        )

    def forward(self, x, return_embeddings=False):
        # Extract tokens from ViT
        cls_token, patch_tokens = self.backbone(x)

        # Fuse Global-Local signals
        embeddings = self.gla(cls_token, patch_tokens)

        if return_embeddings:
            return embeddings

        # Task predictions
        disease_logits = self.disease_head(embeddings)
        attr_logits = self.attr_head(embeddings)

        return disease_logits, attr_logits, embeddings
