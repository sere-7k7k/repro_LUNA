# Spatiotemporal Transcriptome (STT) — Project Context

## A. Core Idea

The goal is to address the scarcity of joint single-cell + spatial + temporal data by combining existing data abundance with generative conversion.

- **Logic 1:** Single-cell + time data (e.g., developmental stages, disease stages) is abundant.
- **Logic 2:** Single-cell-level spatial data is abundant.
- **Logic 3:** Joint single-cell + spatial + time data is scarce.
- **Logic 4:** The existing **LUNA** model can convert single-cell data into single-cell + spatial data.
- **Added-up Logic:** Use **Logic 1 + Logic 4** to address **Logic 3**, then train a **foundation model (FM)** to solve this issue more generally.
- **Methodology:** Use LUNA (tissue reassembly with generative AI) to generate pseudo spatial context from single-cell data and pair it with time-annotated single-cell datasets for STT model training.

**References:**
- LUNA paper: `LUNA_V2_Oct.pdf`
- stVCR paper (Nature Methods): Neural ODE approach for spatiotemporal dynamics — `LUNA_core/papers/stVCR_paper_main.pdf`

---

## B. LUNA Reproduction Findings (2026-03-31)

**Status: Reproduction COMPLETE — matches paper**

LUNA reproduced on MERFISH mouse primary motor cortex (1000 epochs, A100 GPU).
Our Spearman = 0.452 vs paper's 0.448 — essentially identical.

**Key takeaways:**
1. LUNA works — generates plausible spatial coords from gene expression alone. Core Logic 4 is validated.
2. Spatial quality is moderate — global tissue architecture captured, fine-grained placement is noisy.
3. Training is cheap — ~1 hr on A100 per tissue type. Feasible at scale.
4. Still improving at 1000 epochs — extended training likely pushes Spearman to ~0.5+.
5. Performance scales with slice size — larger slices (3000+ cells) work well; small slices (<1500) degrade.

**Files:** `repro_results.md`, `notes/reproduction_comparison.md`, `LUNA_core/outputs_remote/`

---

## C. Open Questions for STT — Detailed Analysis

### Question 1: How noisy can the pseudo-spatial context be before STT model quality suffers?

LUNA's Spearman of ~0.45 means it recovers roughly half the spatial ranking information. The STT foundation model will train on these approximate coordinates as if they were ground truth. The question is whether this noise floor corrupts the downstream model or whether the FM can learn to be robust to it.

**Concrete example:** Consider two L5 IT neurons that are 100 um apart in reality. LUNA might place them 200 um apart or 50 um apart — the pairwise distance ranking is partially preserved but noisy. If the STT model needs to learn "these two cells are neighbors and their expression changes over time in a coordinated way," noisy positions could either (a) add helpful regularization (the model learns expression-based proximity rather than relying on exact coords) or (b) inject false spatial relationships that confuse temporal dynamics.

**How to test:** Train STT on LUNA-generated coords vs ground-truth coords for a tissue where both exist (e.g., MERFISH motor cortex). Compare downstream task performance. The gap tells you how much noise matters.

| | Pros | Cons |
|---|------|------|
| **Tolerate noise (use LUNA as-is)** | Can apply to any scRNA-seq dataset immediately; no extra data needed; fast pipeline | Spatial errors propagate into STT; some cell neighborhoods will be wrong |
| **Reduce noise first (extend training, ensemble, filter)** | Higher fidelity spatial context; more reliable STT training signal | Slower pipeline; diminishing returns past a point; may not be necessary |
| **Sidestep noise (use embeddings instead of coords, see Q3)** | Richer representation; noise is implicit rather than explicit | Harder to interpret; unclear if FM can leverage unstructured embeddings |

---

### Question 2: Per-tissue fine-tuning vs one multi-tissue atlas model?

LUNA can be trained two ways for STT pseudo-spatial generation:

**Option A — Per-tissue fine-tuning:** Train a separate LUNA model for each tissue type (e.g., one for cortex, one for liver, one for lung). Each model specializes in that tissue's spatial structure.

**Option B — One multi-tissue atlas model:** Train a single LUNA on a large multi-tissue atlas (like ABC MERFISH whole brain, 2.85M cells across 147 slices covering many brain regions). Use this one model to generate spatial context for all tissues.

**Concrete example:** Suppose you want spatial coords for a scRNA-seq dataset of mouse hippocampus cells collected at 5 developmental timepoints.

- *Option A:* Find a spatial reference dataset of hippocampus (e.g., 10 MERFISH hippocampus slices). Train LUNA on those slices (~1 hr). Generate coords for your scRNA-seq cells. Repeat for every new tissue.
- *Option B:* Use the pre-trained whole-brain LUNA model. Feed in your hippocampus scRNA-seq cells. The model has seen hippocampus-like regions during training and can generalize. No per-tissue training needed.

The paper already demonstrates Option B works: they trained on the ABC MERFISH atlas and applied it to unseen scRNA-seq CNS data (1.08M cells) with good results (Fig. 4).

| | Pros | Cons |
|---|------|------|
| **Per-tissue fine-tuning** | Higher accuracy for each specific tissue; can leverage small tissue-specific spatial references | Requires a spatial reference dataset for every tissue; doesn't scale to dozens of tissues; redundant training |
| **One multi-tissue model** | Train once, apply everywhere; captures cross-tissue spatial priors; paper demonstrates this works | May underperform on tissues dissimilar to training atlas; needs large multi-tissue spatial atlas; less control per tissue |
| **Hybrid (pre-train multi-tissue, fine-tune per tissue)** | Best of both — broad priors + tissue-specific sharpening | Most complex pipeline; requires both large atlas and per-tissue references |

**Recommendation for STT:** Start with the multi-tissue approach (Option B) since the paper validates it. Fall back to per-tissue fine-tuning only if quality is insufficient for specific tissues.

---

### Question 3: Can we use LUNA's intermediate representations (transformer embeddings) directly, rather than generated coordinates?

The STT pipeline as currently conceived:

```
scRNA-seq (gene expression + time)
    -> LUNA -> predicted (x, y) coordinates
        -> pair with time labels
            -> train STT foundation model
```

The generated (x, y) coordinates are the final output of LUNA's 1000-step reverse diffusion. But LUNA's 8-layer transformer internally builds rich cell embeddings that encode spatial relationships — these embeddings are what allow the model to predict positions in the first place.

The idea: **skip coordinate generation and feed the internal embeddings directly into the STT model.**

**Concrete example:** A cell with 254-gene expression goes through LUNA's transformer. After 8 layers of self-attention across all cells in the tissue, it gets a 256-dimensional embedding vector. This embedding encodes not just "this cell should be at (0.1, -0.3)" but richer context like "this cell is in a neighborhood of L4/5 IT neurons, near the boundary with L6 CT, in a region with high Cux2 expression gradient."

```
Option A (current plan):  gene_expr -> LUNA -> (x, y)           -> STT model
                          254 dims          2 dims

Option B (this idea):     gene_expr -> LUNA encoder -> embedding -> STT model
                          254 dims                    256 dims
```

**Why this might matter:** The 2D coordinates are a lossy compression of the spatial context LUNA learned. Two cells at identical (x, y) in different tissues would look the same to the STT model, but their transformer embeddings would differ because they encode tissue-specific neighborhood context. For the STT foundation model, that richer signal could be more useful than just coordinates.

| | Pros | Cons |
|---|------|------|
| **Use (x, y) coordinates** | Interpretable; easy to validate visually; aligns with established spatial biology workflows; paper metrics directly apply | Only 2 dimensions — lossy; no neighborhood context; rotation/reflection ambiguity after Kabsch alignment |
| **Use transformer embeddings** | 256 dims — much richer signal; encodes neighborhood relationships implicitly; no reverse diffusion needed (faster inference) | Not interpretable; unclear how to validate quality; embeddings may encode training-set-specific artifacts; requires modifying LUNA's inference pipeline to extract intermediate features |
| **Use both (coords + embeddings concatenated)** | Maximum information; STT model can learn to weight each signal | Increases input dimensionality; risk of redundancy; more complex pipeline |

**Technical note:** Extracting embeddings requires a forward pass through LUNA's transformer at a *specific* diffusion timestep (e.g., t=0 or a mid-range t). The choice of timestep affects what the embeddings represent — early timesteps encode coarse structure, late timesteps encode fine positioning. This would need experimentation.

---

## D. Tasks

- [x] Survey existing spatiotemporal data across species and tissues (e.g., mouse development/MERFISH)
- [x] Replicate the LUNA model using open-source repositories
- [ ] Reference the stVCR paper (Neural ODE approach) — understand how it models temporal dynamics
- [ ] Design STT pipeline: decide on spatial representation (coords vs embeddings vs hybrid)
- [ ] Identify candidate scRNA-seq + time datasets for STT training
- [ ] Run LUNA on multi-tissue atlas (ABC MERFISH whole brain) to test scalability
- [ ] Prototype STT model architecture
