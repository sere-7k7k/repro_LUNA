# LUNA Reproduction Results — MERFISH Mouse Primary Motor Cortex

**Date:** 2026-03-31 | **Reproduced by:** sere-7k7k | **Hardware:** AutoDL A100-PCIE-40GB

---

## Summary

LUNA reproduction on MERFISH mouse primary motor cortex **successfully matches the paper's reported metrics**. Our best checkpoint (epoch 999) achieves Spearman = 0.452, compared to the paper's reported 0.448. The model captures global tissue architecture (cortical layering) but produces blurred boundaries between cell-type regions.

---

## Metrics Across Checkpoints

| Epoch | RSSD (lower=better) | Spearman (higher=better) | F1 (higher=better) | Precision |
|------:|---------------------:|-------------------------:|-------------------:|----------:|
| 249   | 20.71                | 0.393                    | 0.247              | 0.247     |
| 499   | 20.12                | 0.416                    | 0.256              | 0.256     |
| 749   | 19.26                | 0.441                    | 0.263              | 0.263     |
| 999   | 18.85                | 0.452                    | 0.269              | 0.269     |

- All metrics improve monotonically — model still improving at epoch 999
- Suggests extended training (2000-3000 epochs) would yield further gains

## Comparison to Paper

| Metric | Paper (reported) | Ours (epoch 999) | Match? |
|--------|:----------------:|:----------------:|:------:|
| Spearman's Rank Correlation | 0.448 | 0.452 | Yes |

The paper reports "average correlation coefficient of 44.8%" on the same setup: 33 training slices (158K cells) from one mouse, 31 test slices (118K cells) from another. Our result (45.2%) is within noise of this.

---

## Training Details

| Parameter | Value |
|-----------|-------|
| Model | 8-layer transformer, 256-dim, 16 heads (8.8M params) |
| Diffusion | 1000 steps, cosine schedule |
| Optimizer | AdamW, lr=5e-4, amsgrad, weight_decay=1e-12 |
| Batch size | 6 slices (~32K cells per batch) |
| Steps/epoch | ~6 (33 slices / batch 6) |
| Total epochs | 1000 |
| Train data | 158,379 cells across 33 slices (254 genes) |
| Test data | 118,036 cells across 31 slices |

## Compute Cost

| Phase | Time | Notes |
|-------|------|-------|
| Training (1000 epochs) | ~58 min | A100-PCIE-40GB |
| Testing (4 checkpoints x 31 slices) | ~80 min | 1000 reverse diffusion steps per slice |
| **Total GPU time** | **~2.3 hours** | |
| AutoDL cost | ~$1-2 USD | A100 hourly rate |

Training is fast; testing is the bottleneck (reverse diffusion sampling is inherently sequential per slice).

---

## Visual Assessment

Scatter plots (true vs predicted cell positions, colored by cell class) were inspected for 3 slices at epoch 999:

**Best slice (slice 249, Spearman=0.59, 4052 cells):**
- Prediction captures cortical layer structure: L2/3 IT at top, L4/5 IT in middle, deeper layers (L6 CT, L6b) below
- Global tissue contour is well-preserved
- Layer boundaries are blurred compared to ground truth

**Worst slice (slice 10, Spearman=0.30, 1160 cells):**
- Smallest test slice — fewer cells makes reconstruction harder
- Rough tissue shape captured but with substantially more scatter
- Cell-type mixing across regions is prominent

**Typical slice (slice 280, Spearman=0.50, 3851 cells):**
- Layered cortical structure clearly visible in prediction
- Contour and cell-type ordering largely correct
- Some positional noise within layers

**Patterns:**
- Performance correlates with slice size (more cells = better reconstruction)
- The model correctly places cell types in approximately the right spatial regions
- Fine-grained cell placement within regions remains noisy
- Tissue contour/shape is well-captured even when internal arrangement is imperfect

---

## Per-Slice Metrics (Epoch 999)

| Slice | Cells | RSSD | Spearman | F1 |
|-------|------:|-----:|---------:|---:|
| slice249 | 4052 | 18.04 | 0.592 | 0.303 |
| slice270 | 4081 | 18.89 | 0.550 | 0.291 |
| slice229 | 5047 | 19.83 | 0.549 | 0.307 |
| slice289 | 4360 | 19.58 | 0.539 | 0.299 |
| slice201 | 3733 | 18.43 | 0.531 | 0.285 |
| slice300 | 3780 | 16.81 | 0.514 | 0.291 |
| slice319 | 2800 | 16.16 | 0.503 | 0.269 |
| slice280 | 3851 | 19.70 | 0.502 | 0.281 |
| slice1   | 1706 | 13.93 | 0.340 | 0.242 |
| slice20  |  670 |  9.34 | 0.305 | 0.210 |
| slice10  | 1160 | 12.12 | 0.304 | 0.211 |

(Top 8 and bottom 3 shown. Full data in results CSVs.)

---

## Reproducibility Issues Encountered

1. **Dependency hell:** `lightning` pulled `torch 2.8.0`, breaking PyG. Fixed by pinning `lightning<2.1`, `torchmetrics<1.3`, `numpy<2`.
2. **Windows incompatibilities:** `multiprocessing_context="fork"` and `num_workers=32` hardcoded — Linux-only. Not relevant to remote GPU training.
3. **scipy version:** RSSD metric crashes with scipy >= 1.10 due to API changes. Pinned `scipy==1.9.1`.
4. **No README version pins:** The README specifies Python 3.9 and torch 2.0.1 but doesn't pin other critical dependencies.

**Reproducibility verdict:** Reproducible with careful dependency management. The code works as described and matches reported metrics. Main friction is dependency resolution, not code bugs.

---

## Implications for STT Project

1. **LUNA works as advertised** — it can generate plausible spatial coordinates from gene expression alone
2. **Quality is moderate** — Spearman ~0.45 means spatial structure is partially recovered but noisy. For STT, the pseudo-spatial context will be approximate, not precise.
3. **Training is cheap** — ~1 hour on A100 for a new tissue. This is feasible for generating spatial contexts across many tissues.
4. **Extended training helps** — monotonic improvement suggests 2000-3000 epochs may push Spearman to ~0.5+
5. **Slice size matters** — LUNA works better with more cells per slice. Small/sparse tissues may underperform.
6. **The diffusion framework is elegant** — rotation-invariant loss (pairwise distance MSE) is a clean design choice. Worth understanding deeply for potential modifications.

---

## File Locations

- Results: `LUNA_core/outputs_remote/MERFISH_mouse_cortex/model_00-19-18-MERFISH_epoch_*/`
- Training log: `logs/luna_train.log`
- Analysis script: `analyze_results.py`
- This report: `repro_results.md`
