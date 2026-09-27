import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
from ..utils.paths import paths

class ExperimentLogger:
    """Handles logging of configs, metrics, and checkpoints for research reproducibility."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.run_dir = paths.get_output_path(f"runs/{self.run_id}")
        self.run_dir.mkdir(parents=True, exist_ok=True)

        # Save resolved config immediately
        self._save_config()

    def _save_config(self):
        config_path = self.run_dir / "config.json"
        with open(config_path, 'w') as f:
            json.dump(self.config, f, indent=4)

    def log_metrics(self, epoch: int, metrics: Dict[str, float], stage: str = "train"):
        """Logs metrics to a JSONL file."""
        log_file = self.run_dir / f"{stage}_metrics.jsonl"
        entry = {"epoch": epoch, **metrics}
        with open(log_file, 'a') as f:
            f.write(json.dumps(entry) + "\n")

    def save_checkpoint(self, model, optimizer, epoch: int, is_best: bool = False):
        """Saves model state."""
        state = {
            'epoch': epoch,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
        }
        torch.save(state, self.run_dir / "checkpoint_latest.pt")
        if is_best:
            torch.save(state, self.run_dir / "checkpoint_best.pt")
