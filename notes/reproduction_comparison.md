# LUNA MERFISH Reproduction Comparison

## Setup Comparison

| Feature | Paper / Repo Demo | Our Reproduction | STT Next Steps |
|---------|-------------------|------------------|----------------|
| **Dataset** | MERFISH mouse primary motor cortex (Zhang et al., Nature 2021) | Same | Same dataset first; then expand to multi-tissue atlases (e.g., ABC MERFISH whole brain, 2.85M cells) |
| **Train/Test Split** | 33 slices (158K cells) train, 31 slices (118K cells) test, cross-animal | Same | Same split for benchmarking; later use all slices for STT pseudo-spatial generation |
| **Epochs** | 1000 (notebook default); 3000 (config default) | 1000 | 2000-3000 (model still improving at 1000; worth pushing further) |
| **Batch Size** | 6 (for 24GB GPU, e.g., RTX 3090) | 6 | Same |
| **GPU** | RTX 3090 (24GB), ~2 hr training | A100-PCIE-40GB, ~58 min train + ~80 min test | A100 preferred for speed; RTX 3090 sufficient |
| **Mode** | `train_and_test` (notebook) or `test_only` (with pre-trained checkpoints) | `train_and_test`, plus verified `test_only` separately | `train_and_test` for new tissues; `test_only` for inference at scale |
| **Checkpoints** | Save every 250 epochs (4 checkpoints at 1000 epochs) | Same (epoch 249, 499, 749, 999) | Same; pick best checkpoint for downstream use |
| **Wandb** | Enabled by default | Disabled (`general.wandb=disabled`) — avoids login friction | Optional; not critical for STT workflow |
| **Dependencies** | README pins Python 3.9, torch 2.0.1 — nothing else pinned | Pinned lightning<2.1, torchmetrics<1.3, scipy==1.9.1, numpy<2 | Use our pinned versions to avoid repeating dependency hell |
| **Key Metric (Spearman)** | 0.448 (paper Fig. 3b) | 0.452 (epoch 999) | Target: 0.50+ with extended training |

## Metrics Comparison

| Metric | Paper | Ours (epoch 999) | Notes |
|--------|:-----:|:-----------------:|-------|
| Spearman's Rank Correlation | 0.448 | 0.452 | Match. Averaged over 31 test slices. |
| RSSD | Not directly reported in main text | 18.85 | Reported in supplementary figures only. |
| F1 / Precision | Not directly reported in main text | 0.269 / 0.269 | See note below on why these are identical. |

## Why F1 = Precision (Metric Design Issue)

In our results, F1 and Precision are identical across all checkpoints. This is **not a bug** — it's a structural property of how `compute_contact` works in `metrics/evaluation_statistics.py`:

```
1. Take pairwise distance matrices (true and predicted)
2. Binarize BOTH at their own 10th-percentile threshold
3. Compute precision and F1 on the binary labels
```

Because both arrays are thresholded at their **own** 10th quantile, both end up with ~10% positives. This forces the number of false positives (FP) to approximately equal the number of false negatives (FN), which makes Precision ~ Recall, and therefore F1 ~ Precision ~ Recall.

**Example:** With 1000 cell pairs, both true and predicted labels have ~100 positives. Even if overlap is imperfect, FP and FN are balanced by construction — predicting 100 positives against 100 true positives guarantees FP = FN = (100 - TP).

**Implication:** F1 and Precision are redundant here. They measure one thing: *what fraction of the closest 10% of cell pairs in ground truth are also in the closest 10% of predicted pairs*. **RSSD and Spearman are the more informative metrics** for evaluating LUNA output quality.

## What to Try Next (STT-Motivated)

| Experiment | Purpose | Priority |
|------------|---------|----------|
| Train 2000-3000 epochs | Model still improving; check if Spearman reaches 0.50+ | High |
| Train on ABC MERFISH whole brain (147 slices, 2.85M cells) | Paper's full-scale setup; needed for multi-region STT | High |
| Ablation: 4 layers instead of 8 | Check if smaller model suffices — faster training for STT at scale | Medium |
| Ablation: 128-dim instead of 256 | Same rationale | Medium |
| Subset: train on 10 slices, test on 31 | How sensitive is LUNA to training data quantity? Informs STT feasibility for data-scarce tissues | Medium |
| Extract transformer embeddings | Use 256-dim cell embeddings instead of 2D coords as spatial context for STT | Exploratory |
| Test on non-cortex tissue | Verify LUNA generalizes beyond layered cortical structures | Medium |
