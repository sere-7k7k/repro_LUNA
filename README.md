# LUNA Reproduction

Independent reproduction of [LUNA](https://github.com/mlbio-epfl/LUNA) (tissue reassembly via diffusion-based generative AI) on the MERFISH mouse primary motor cortex dataset. Part of the Spatiotemporal Transcriptome (STT) project.

## Key Result

| Metric | Paper | Ours (1000 epochs) |
|--------|:-----:|:-------------------:|
| Spearman's Rank Correlation | 0.448 | **0.452** |

Reproduction matches the paper. See `notes/repro_results.md` for full metrics across checkpoints.

## Quick Start

### 1. Environment Setup

```bash
conda create -n LUNA python=3.9 -y
conda activate LUNA

# Core dependencies (order matters)
pip install torch==2.0.1 --index-url https://download.pytorch.org/whl/cu118
pip install torch_geometric torch_scatter torch_sparse -f https://data.pyg.org/whl/torch-2.0.1+cu118.html
pip install "lightning<2.1" "torchmetrics<1.3" "scipy==1.9.1" "numpy<2"
pip install scanpy hydra-core pyrootutils
```

### 2. Download Data

Download [MERFISH mouse cortex dataset](https://drive.google.com/file/d/1j6W5NZV56_W3kO_UxXEtFv1nIlwUksLi/view?usp=drive_link) and extract to `LUNA_core/data/MERFISH_mouse_cortex/`.

### 3. Train + Test

```bash
cd LUNA_core
python main.py general.name=MERFISH_mouse_cortex \
    general.wandb=disabled \
    dataset.gene_columns_start=0 \
    dataset.gene_columns_end=254 \
    distribute.gpus_per_node=[0] \
    train.batch_size=6 \
    dataset.train_data_path=/path/to/MERFISH_mouse_cortex_train.csv \
    dataset.test_data_path=/path/to/MERFISH_mouse_cortex_test.csv \
    test.save_dir=/path/to/save/results
```

- ~1 hr training + ~1.5 hr testing on A100 (batch_size=6)
- ~2 hr training on RTX 3090 (batch_size=6)

### 4. Analyze Results

```bash
# Update the base path in the script, then:
python notes/analyze_results.py
```

## Repo Structure

```
repro_LUNA/
├── README.md                  # This file
├── .gitignore
│
├── LUNA_core/                 # Upstream LUNA code (from mlbio-epfl/LUNA)
│   ├── README.md              #   Original README with full docs
│   ├── main.py                #   Entry point
│   ├── configs/               #   Hydra configs (experiment, model, train, test)
│   ├── models/                #   Transformer + self-attention layers
│   ├── metrics/               #   RSSD, Spearman, Contact F1 evaluation
│   ├── datasets/              #   Data module (batching, padding)
│   ├── utils/
│   │   ├── data/              #     Data loading, normalization, DataHolder
│   │   └── diffusion_model/   #     Noise schedule, training loop, sampling, testing
│   ├── example/               #   Jupyter notebooks (train_and_test, test_only)
│   ├── papers/                #   stVCR reference paper
│   ├── smoke_test.py          #   CPU smoke test (no GPU needed)
│   └── data/                  #   Dataset directory (not tracked, download separately)
│
└── notes/                     # Reproduction analysis and STT project docs
    ├── repro_results.md       #   Full reproduction report (metrics, visual assessment, compute cost)
    ├── reproduction_comparison.md  #   Paper vs ours vs next steps comparison table
    ├── STT_project_context.md #   STT project motivation + open research questions
    └── analyze_results.py     #   Script to compute per-checkpoint metrics from result CSVs
```

## Model Overview

LUNA uses a **diffusion model** to generate 2D cell coordinates from gene expression:

1. **Training**: Learn to denoise cell positions via an 8-layer transformer (8.8M params). Loss is MSE over pairwise distance matrices (rotation-invariant).
2. **Inference**: Start from random noise, reverse-diffuse for 1000 steps to generate spatial coordinates conditioned on gene expression.

| Parameter | Value |
|-----------|-------|
| Transformer layers | 8 |
| Hidden dim | 256 |
| Attention heads | 16 |
| Diffusion steps | 1000 |
| Train data | 158K cells, 33 slices, 254 genes |
| Test data | 118K cells, 31 slices |

## Dependency Pinning

The original repo doesn't pin all dependencies. These pins are critical:

| Package | Pin | Why |
|---------|-----|-----|
| `torch` | `2.0.1+cu118` | PyG wheels require exact match |
| `lightning` | `<2.1` | Later versions pull torch 2.8, breaking PyG |
| `scipy` | `==1.9.1` | RSSD metric uses removed API in scipy >= 1.10 |
| `numpy` | `<2` | numpy 2.0 breaks multiple downstream packages |

## Context

This reproduction is part of the **Spatiotemporal Transcriptome (STT)** project, which aims to combine single-cell temporal data with LUNA-generated pseudo-spatial context to build a spatiotemporal foundation model. See `notes/STT_project_context.md` for details.

## Credits

- **LUNA**: [mlbio-epfl/LUNA](https://github.com/mlbio-epfl/LUNA) by Brbic Lab, EPFL
- **Paper**: "LUNA: Generative AI Model for Tissue Reassembly" (bioRxiv 2025)
