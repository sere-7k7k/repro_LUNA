# Handbook: Pull Upstream Repo Into a Local Workspace and Publish Your Own GitHub Copy

## Goal

Start from an existing local folder, pull an upstream GitHub repo into it, keep your own local notes/files, and publish the result to your own public GitHub repo.

## Step-by-step

1. Pick the upstream repo and your target repo URL.
   - Example upstream: `https://github.com/mlbio-epfl/LUNA.git`
   - Example target: `https://github.com/sere-7k7k/repro_LUNA.git`

2. Clone the upstream repo into a temporary folder.

```powershell
git clone --depth 1 https://github.com/mlbio-epfl/LUNA C:\path\to\temp\LUNA_upstream_tmp
```

3. Copy the upstream working tree into your real workspace, excluding `.git`.

```powershell
Get-ChildItem -Force C:\path\to\temp\LUNA_upstream_tmp |
  Where-Object { $_.Name -ne '.git' } |
  Copy-Item -Destination C:\path\to\your\workspace -Recurse -Force
```

4. Initialize git in your real workspace.

```powershell
cd C:\path\to\your\workspace
git init -b main
```

5. Add remotes.

```powershell
git remote add upstream https://github.com/mlbio-epfl/LUNA.git
git remote add origin https://github.com/sere-7k7k/repro_LUNA.git
```

6. Fetch upstream history and anchor `main` to it.

```powershell
git fetch upstream
git reset upstream/main
```

7. Add your local-only files on top.
   - Examples: papers, notes, setup docs, configs for reproduction.

8. Set the local commit identity if needed.

```powershell
git config user.name "sere-7k7k"
git config user.email "sere-7k7k@users.noreply.github.com"
```

9. Create the GitHub repo.

```powershell
gh repo create sere-7k7k/repro_LUNA --public
```

If `origin` already exists, do not use `--remote origin` again.

10. Commit and push.

```powershell
git add .
git commit -m "Add upstream LUNA and local reproduction context"
git push -u origin main
```

## Common failures

- `gh auth status` says the token is invalid:
  - Run `gh auth login -h github.com`

- `gh repo create ... --remote origin` fails with remote-add errors:
  - The repo may already exist.
  - Check `git remote -v`
  - Then use `git push -u origin main`

- Git says `dubious ownership`:
  - Mark the repo as safe:

```powershell
git config --global --add safe.directory C:/path/to/your/workspace
```

- Checkout fails because untracked files would be overwritten:
  - If those files were copied from upstream, use the `git reset upstream/main` approach instead of branch checkout.

## Minimal verification

```powershell
git status --short --branch
git remote -v
git log --oneline --decorate -1
```
