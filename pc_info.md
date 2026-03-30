# PC / Local Environment

## What this machine is good for

- Windows 11 laptop (`Surface Laptop 4`, AMD Ryzen 7, `16 GB` RAM).
- Good for reading papers, planning experiments, light preprocessing, and smoke tests.
- Assume **no reliable local CUDA GPU for LUNA training**. Anything beyond tiny CPU checks should be treated as a remote-GPU task.

## Constraints that matter for this repo

- This repo is for a **small-scale LUNA reproduction / understanding pass**, not full atlas-scale replication.
- Prefer tiny demo subsets, short runs, and resumable scripts.
- Keep memory use conservative; avoid assuming large local RAM or VRAM.
- If a task needs long training, fast iteration, or CUDA, plan for remote compute.

## Network note

- The user often keeps VPN enabled because some AI tools depend on it.
- Do not suggest disabling VPN unless it is clearly the source of a problem.
