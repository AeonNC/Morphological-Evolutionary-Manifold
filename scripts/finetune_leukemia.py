import argparse
import yaml
import torch
from pathlib import Path
from mem.models.mem_vit import MEMViT
from mem.training.trainer import MEMTrainer
from mem.data.manifest import MasterManifest
from mem.data.splitting import GroupAwareSplitter
from torch.utils.data import DataLoader, Dataset

class LeukemiaDataset(Dataset):
    """Dataset for fine-tuning on AML/ALL disease labels."""
    def __init__(self, df, transform=None):
        self.df = df
        self.transform = transform

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        # Mock image and labels for pipeline validation
        image = torch.randn(3, 224, 224)
        disease = torch.tensor(1 if row['leukemia_category'] == 'AML' else 0, dtype=torch.long)
        attr = torch.randn(11) # Random attrs during fine-tuning if not provided

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

    # IMPORTANT: Use patient_id to prevent leakage
    splitter = GroupAwareSplitter(manifest)
    df_split = splitter.split(group_column='patient_id')

    train_df = df_split[df_split['split'] == 'train']
    val_df = df_split[df_split['split'] == 'val']

    train_loader = DataLoader(LeukemiaDataset(train_df), batch_size=config['batch_size'], shuffle=True)
    val_loader = DataLoader(LeukemiaDataset(val_df), batch_size=config['batch_size'])

    # 2. Setup Model
    # Load pretrained weights from WBCAtt stage
    model = MEMViT()
    # model.load_state_dict(torch.load('outputs/checkpoints/wbcatt_best.pt'))

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
