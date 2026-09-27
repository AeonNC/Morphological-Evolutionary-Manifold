import argparse
import yaml
import torch
from pathlib import Path
from mem.models.mem_vit import MEMViT
from mem.training.trainer import MEMTrainer
from mem.data.manifest import MasterManifest
from mem.data.splitting import GroupAwareSplitter
from torch.utils.data import DataLoader, Dataset

class MorphologyDataset(Dataset):
    """Dataset for pretraining on WBCAtt morphology attributes."""
    def __init__(self, df, image_dir, transform=None):
        self.df = df
        self.image_dir = Path(image_dir)
        self.transform = transform

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        img_path = Path(row['image_path'])
        # In real implementation, use PIL/OpenCV to load and transform
        # For now, we provide a mock tensor to enable pipeline testing
        image = torch.randn(3, 224, 224)

        # Morphology attributes (11 values)
        attr = torch.tensor([1.0] * 11, dtype=torch.float32)
        # Disease label (mock for pretraining)
        disease = torch.tensor(0, dtype=torch.long)

        return image, {"attr": attr, "disease": disease}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, required=True)
    args = parser.parse_args()

    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)

    # 1. Setup Data
    manifest = MasterManifest()
    df = manifest.load()

    splitter = GroupAwareSplitter(manifest)
    df_split = splitter.split(group_column='record_id') # Use record_id for WBCAtt

    train_df = df_split[df_split['split'] == 'train']
    val_df = df_split[df_split['split'] == 'val']

    train_loader = DataLoader(MorphologyDataset(train_df, ""), batch_size=config['batch_size'], shuffle=True)
    val_loader = DataLoader(MorphologyDataset(val_df, ""), batch_size=config['batch_size'])

    # 2. Setup Model
    model = MEMViT(num_attrs=11)

    # 3. Setup Trainer
    trainer = MEMTrainer(model, config)

    # 4. Run Loop
    for epoch in range(config['epochs']):
        train_metrics = trainer.train_epoch(train_loader, {"attr": "attr", "disease": "disease"})
        val_metrics = trainer.validate(val_loader, {"attr": "attr", "disease": "disease"})

        trainer.logger.log_metrics(epoch, train_metrics, "train")
        trainer.logger.log_metrics(epoch, val_metrics, "val")

        print(f"Epoch {epoch} | Train Loss: {train_metrics['loss_total']:.4f} | Val Loss: {val_metrics['loss_total']:.4f}")

if __name__ == "__main__":
    main()
