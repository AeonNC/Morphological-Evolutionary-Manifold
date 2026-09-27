import os
from pathlib import Path
import yaml

class ProjectPaths:
    """Centralized path management for the MEM project."""

    def __init__(self, config_path="configs/base.yaml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.root = Path(__file__).parent.parent.parent.absolute()
        self.data_root = Path(self.config.get('data_root', 'data/'))
        self.output_root = Path(self.config.get('output_root', 'outputs/'))
        self.config_root = Path(self.config.get('config_root', 'configs/'))

    @property
    def raw_data(self) -> Path:
        return self.data_root / "raw"

    @property
    def processed_data(self) -> Path:
        return self.data_root / "processed"

    @property
    def manifests(self) -> Path:
        return self.data_root / "manifests"

    @property
    def checkpoints(self) -> Path:
        return Path(self.config.get('checkpoint_dir', 'outputs/checkpoints/'))

    def get_dataset_path(self, dataset_name: str) -> Path:
        return self.raw_data / dataset_name

    def get_output_path(self, subfolder: str) -> Path:
        return self.output_root / subfolder

paths = ProjectPaths()
