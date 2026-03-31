"""Analyze LUNA training results across checkpoints."""
import csv, os, glob

base = "C:/Users/Sere_/playground/projects/LUNA/LUNA_core/outputs_remote/MERFISH_mouse_cortex"
for d in sorted(glob.glob(os.path.join(base, "model_*"))):
    f = os.path.join(d, "MERFISH_mouse_cortex_results.csv")
    if not os.path.exists(f):
        continue
    epoch = d.split("epoch_")[-1]
    with open(f) as fh:
        rows = list(csv.DictReader(fh))
    n = len(rows)
    rssd = sum(float(r["test/rssd_absolute"]) for r in rows) / n
    spr = sum(float(r["test/Spearman's Rank Correlation (Median)"]) for r in rows) / n
    f1 = sum(float(r["test/F1"]) for r in rows) / n
    prec = sum(float(r["test/precision"]) for r in rows) / n
    print(f"Epoch {epoch:>4s}: {n:>2d} slices | RSSD={rssd:.4f} | Spearman={spr:.4f} | F1={f1:.4f} | Precision={prec:.4f}")
