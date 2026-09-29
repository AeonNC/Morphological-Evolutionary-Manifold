import torch
import torch.nn as nn
import timm
from typing import Optional, Dict, Any

class MEMBackbone(nn.Module):
    """
    Flexible backbone wrapper for ViT and CNN models.
    """
    def __init__(self, model_name: str = "vit_small_patch16_224", pretrained: bool = True):
        super().__init__()
        self.model = timm.create_model(model_name, pretrained=pretrained, num_classes=0)
        self.embed_dim = self.model.num_features

    def forward(self, x):
        # Returns the global embedding (CLS token)
        return self.model(x)

class FrozenDINOv2(nn.Module):
    """
    Baseline using frozen DINOv2 embeddings.
    """
    def __init__(self, model_name: str = "dinov2_vits14"):
        super().__init__()
        self.model = torch.hub.load('facebookresearch/dinov2', model_name)
        self.model.eval()
        for param in self.model.parameters():
            param.requires_grad = False

    def forward(self, x):
        return self.model(x)
