# Remote Training Workflow Reference

This is a **generic AutoDL-style workflow note for this LUNA repo only**. The old project names, server names, paths, and paper-specific details from the past example are **not** authoritative here.

## When remote training is justified

- Use remote GPU only if the local machine cannot run the job in a reasonable way.
- For this repo, first aim for:
  - CPU or very small local smoke tests.
  - Small demo subsets that validate the pipeline.
  - Understanding LUNA's inputs, outputs, and failure modes before scaling up.

## Minimal remote workflow

1. Prepare a small, reproducible run locally first.
2. Sync only what is needed:
   - code
   - environment / dependency spec
   - configs
   - subset definition or data manifest
   - run script
3. On the remote machine, verify paths and environment before launching training.
4. Start with a tiny smoke run before any longer job.
5. Save logs, checkpoints, exact commands, and dataset subset details.
6. Pull results back to the local repo and summarize what worked / failed.

## Agent rules for remote work

- Do not assume any fixed remote server name, SSH alias, path, or repo layout.
- If remote resources are introduced later, inspect them first and document the actual paths in use.
- Treat remote systems cautiously: read first, and do not make writes that matter unless the task clearly requires it.
- Keep runs resumable and easy to compare across subsets.

## Repo-specific goal

The target is **not** to reproduce every large-scale claim from the LUNA paper. The target is to check whether the method can be reproduced on a smaller subset, understand the pipeline end to end, and learn what would be required to scale later.
