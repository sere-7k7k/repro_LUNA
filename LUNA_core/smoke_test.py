"""Local CPU smoke test: verify data loading + model init without DDP.
Patches Windows-incompatible DataLoader settings (fork, num_workers=32).
"""
import os
os.environ['MASTER_ADDR'] = 'localhost'
os.environ['MASTER_PORT'] = '12355'
os.environ['WORLD_SIZE'] = '1'
os.environ['RANK'] = '0'
os.environ['LOCAL_RANK'] = '0'

# Patch the DataLoader before anything imports it
import utils.data.abstract_datatype as adt
from torch.utils.data import DataLoader as _DL

_orig_create = adt.AbstractDataModule._create_dataloader
def _patched_create(self, dataset, batch_size):
    return _DL(dataset, batch_size=batch_size, shuffle=True,
               num_workers=0, pin_memory=False, collate_fn=self.collate)
adt.AbstractDataModule._create_dataloader = _patched_create

import hydra
from omegaconf import DictConfig
import torch
import pytorch_lightning as pl
from utils.diffusion_model.setup.setup import setup_dataset, setup_model


@hydra.main(version_base="1.3", config_path="./configs", config_name="config")
def main(cfg: DictConfig):
    pl.seed_everything(0)

    # 1. Data loading
    print("[SMOKE] Loading dataset...")
    datamodule, dataset_infos = setup_dataset(cfg)
    print(f"[SMOKE] Dataset loaded OK")
    print(f"[SMOKE]   num_genes={dataset_infos.num_genes}, num_classes={dataset_infos.num_cell_class}")

    # 2. Model init
    print("[SMOKE] Initializing model...")
    model = setup_model(cfg, dataset_infos)
    n_params = sum(p.numel() for p in model.parameters())
    print(f"[SMOKE] Model: {n_params:,} parameters")

    # 3. One train batch (just loading, no forward — too slow on CPU with 32K cells)
    print("[SMOKE] Getting one train batch...")
    train_loader = datamodule.train_dataloader()
    batch = next(iter(train_loader))
    print(f"[SMOKE] Batch node_features: {batch.node_features.shape}")
    print(f"[SMOKE] Batch positions:     {batch.positions.shape}")
    print(f"[SMOKE] Batch cell_class:    {batch.cell_class.shape}")
    print(f"[SMOKE] Batch size (slices): {batch.batch.max().item() + 1}")

    print("[SMOKE] === ALL CHECKS PASSED ===")
    print("[SMOKE] Forward pass skipped (too slow on CPU with 32K cells per batch).")
    print("[SMOKE] Ready for GPU training on remote.")


if __name__ == "__main__":
    main()
