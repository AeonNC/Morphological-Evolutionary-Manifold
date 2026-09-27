import torch
import torch.nn as nn
from timm import create_model
from typing import Optional, Union

class ViTBackbone(nn.Module):
    """
    Flexible ViT Backbone using timm.
    Supports extraction of both the CLS token and patch tokens for GLA.
    """
    def __init__(self, model_name: str = 'vit_small_patch16_224', pretrained: bool = True):
        super().__init__()
        # We use timm to load the base ViT
        self.model = create_model(model_name, pretrained=pretrained, num_classes=0)
        self.embed_dim = self.model.embed_dim

    def forward(self, x):
        # For most timm ViTs, forward_features returns (B, N, C)
        # where N = 1 (CLS) + num_patches
        features = self.model.forward_features(x)

        cls_token = features[:, 0, :] # (B, C)
        patch_tokens = features[:, 1:, :] # (B, num_patches, C)

        return cls_token, patch_tokens

class ResNetBaseline(nn.Module):
    """ResNet-50 baseline for morphology representation."""
    def __init__(self, embed_dim: int = 512):
        super().__init__()
        self.backbone = create_model('resnet50', pretrained=True, num_classes=0, global_pool='avg')
        # Ensure output is embed_dim
        if self.backbone.num_features != embed_dim:
            self.proj = nn.Linear(self.backbone.num_features, embed_dim)
        else:
            self.proj = nn.Identity()

    def forward(self, x):
        feat = self.backbone(x)
        return self.proj(feat)

class EfficientNetBaseline(nn.Module):
    """EfficientNet-B0 baseline for morphology representation."""
    def __init__(self, embed_dim: int = 512):
        super().__init__()
        self.backbone = create_model('efficientnet_b0', pretrained=True, num_classes=0, global_pool='avg')
        if self.backbone.num_features != embed_dim:
            self.proj = nn.Linear(self.backbone.num_features, embed_dim)
        else:
            self.proj = nn.Identity()

    def forward(self, x):
        feat = self.backbone(x)
        return self.proj(feat)
