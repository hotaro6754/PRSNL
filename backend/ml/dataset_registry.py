import os
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel

logger = logging.getLogger('DatasetRegistry')

class DatasetMetadata(BaseModel):
    dataset_id: str
    source: str  # e.g., 'huggingface'
    type: str    # e.g., 'url', 'email', 'sms'
    version: str
    description: str
    downloaded_at: datetime
    record_count: int
    schema_version: str

class DatasetRegistry:
    def __init__(self, registry_path: str = "data/registry"):
        self.registry_path = registry_path
        os.makedirs(self.registry_path, exist_ok=True)
        self.metadata_file = os.path.join(self.registry_path, "datasets.json")
        self._load_registry()

    def _load_registry(self):
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r') as f:
                    data = json.load(f)
                    self.datasets = {k: DatasetMetadata(**v) for k, v in data.items()}
            except Exception as e:
                logger.error(f"Failed to load dataset registry: {e}")
                self.datasets = {}
        else:
            self.datasets = {}

    def _save_registry(self):
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump({k: v.model_dump(mode='json') for k, v in self.datasets.items()}, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save dataset registry: {e}")

    def register_dataset(self, metadata: DatasetMetadata) -> bool:
        self.datasets[metadata.dataset_id] = metadata
        self._save_registry()
        logger.info(f"Registered dataset {metadata.dataset_id}")
        return True

    def get_dataset(self, dataset_id: str) -> Optional[DatasetMetadata]:
        return self.datasets.get(dataset_id)

    def download_huggingface_dataset(self, hf_repo: str, dataset_id: str, type_val: str, split: str = 'train', local_dir: str = 'data/offline_hf'):
        """
        Integrates Hugging Face strictly as an OFFLINE dataset/evaluation source.
        Downloads dataset and registers it locally.
        """
        try:
            from datasets import load_dataset
        except ImportError:
            logger.error("datasets library required for huggingface offline integration. Run pip install datasets")
            return None
            
        os.makedirs(local_dir, exist_ok=True)
        logger.info(f"Downloading {hf_repo} ({split}) to offline storage at {local_dir}...")
        
        # Load dataset offline or download to local cache
        ds = load_dataset(hf_repo, split=split, cache_dir=local_dir)
        
        # Save to csv for offline local ML usage
        csv_path = os.path.join(local_dir, f"{dataset_id}.csv")
        ds.to_csv(csv_path)
        
        metadata = DatasetMetadata(
            dataset_id=dataset_id,
            source=f"huggingface:{hf_repo}",
            type=type_val,
            version="1.0",
            description=f"Offline cached dataset from {hf_repo}",
            downloaded_at=datetime.now(),
            record_count=len(ds),
            schema_version="1.0"
        )
        self.register_dataset(metadata)
        logger.info(f"Offline dataset downloaded to {csv_path} and registered.")
        return csv_path
