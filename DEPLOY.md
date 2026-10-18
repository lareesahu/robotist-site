# Deployment Pipeline — Robotist

## How It Works

This repository uses a **GitHub → Render auto-deploy pipeline**. Every commit pushed to the `main` branch automatically triggers a fresh deploy on Render. No manual steps are required after pushing.

```
Code change → git commit → git push to main → Render detects push → re-deploys automatically
```

---

## Account Setup (Important — Two Accounts)

This project spans two separate accounts. Understanding this prevents future confusion:

| Platform | Account | Notes |
|---|---|---|
| GitHub | `lareesahu` | Repo owner for `lareesahu/robotist-ecommerce` |
| GitHub | `lareesawho` | Original repo owner (transferred; `lareesahu` added as admin) |
| Render | `lareesa@pulse-branding.com` | The Render account that hosts the Robotist service |

**Login for Render:** Use `lareesa@pulse-branding.com` with password `Evolveyourbrand2021`. The GitHub OAuth button on Render will not work reliably — use email/password directly.

---

## What Gets Deployed

| Service | Type | URL | Render Service ID |
|---|---|---|---|
| `robotist` | Static web | [www.robotist.com.au](https://www.robotist.com.au) | `srv-d7egikd7vvec73f79q80` |

The service is defined in `render.yaml` at the root of this repo with `autoDeploy: true`.

---

## The Blueprint File

The file `render.yaml` at the root of this repo is the **Render Blueprint** — it tells Render which branch to watch, where the static files are (`staticPublishPath: .`), and that it should auto-deploy on every push.

**Critical rule:** If `autoDeploy: true` is ever removed or the file is deleted, auto-deploy stops. Render will only deploy manually from the dashboard.

---

## Branch

- **Static site (`robotist`):** watches `main`

Pushes to any other branch (e.g. `claude/...` feature branches) do **not** trigger a deploy.

---

## GitHub Actions: Automatic Image Compression

This repo has a GitHub Actions workflow at `.github/workflows/compress-images.yml`.

**What it does:** Whenever a push to `main` (or a pull request) includes image files (`.jpg`, `.jpeg`, `.png`, `.webp`, `.gif`), the action automatically compresses them using `calibreapp/image-actions` and commits the optimised versions back to the branch before Render picks them up.

**Quality settings:**
- JPEG / WebP: quality 82 (visually near-lossless, ~40–60% smaller)
- PNG: compression level 5

**Note:** This action only runs when image files are changed. Text-only commits skip it entirely.

> **History note:** This workflow was accidentally deleted in the "Full SEO/GEO implementation" commit on Apr 14 2026. It was restored on Jun 23 2026. The file exists locally but requires a GitHub token with `workflows` permission to push via CLI — push it manually via the GitHub web UI at `https://github.com/lareesahu/robotist-ecommerce/new/main/.github/workflows` if needed.

---

## What Broke and Why (Jun 2026)

The auto-deploy stopped working because a **manual rollback** was triggered on Jun 22 2026 in the Render dashboard. Render automatically switches the service to "Manual Deploy" mode after a rollback is performed. The fix was to go back into Render Settings → Deploy → Auto-Deploy and set it back to **"On Commit"**.

---

## Troubleshooting Auto-Deploy

If a push is not triggering a deploy on Render:

1. **Check Render Settings → Deploy → Auto-Deploy** — must be set to **"On Commit"**, not "Off" or "After CI Checks Pass".
2. **Check the branch** — the push must be to `main`, not another branch.
3. **Check Render dashboard** → service → **Events** tab to see if the deploy was triggered.
4. **Check the GitHub webhook** — Render registers a webhook on the repo. Go to GitHub → repo Settings → Webhooks and confirm a Render webhook is listed and showing green ticks.
5. **Re-sync the blueprint** — in Render dashboard, go to the service → Settings → scroll to "Blueprint" and click "Sync" to force Render to re-read `render.yaml`.
6. **Login reminder** — to access Render for Robotist, log in at [dashboard.render.com](https://dashboard.render.com) using email `lareesa@pulse-branding.com` (not GitHub OAuth).
