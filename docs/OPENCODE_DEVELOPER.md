# OpenCode — optional FrontierLab developer assistant

Status 2026-10-27: Project configuration only, OpenCode was NOT installed or used by this change.

Official project: https://github.com/anomalyco/opencode
Official NVIDIA model setup: https://opencode.ai/docs/providers
Official permissions: https://opencode.ai/docs/permissions/
Official agents: https://opencode.ai/docs/agents/

## Purpose
Use OpenCode for local code review, scoped patches and reproducible unit tests. It is NOT the validated scientific agent and does not satisfy the Meta Hackathon model usage condition. No OpenCode process runs inside the public HF Space.

## Safer defaults in opencode.json
- All tools default to asking for approval; ordinary non-secret project reads are allowed.
- File edits and general shell commands require approval.
- Git pushes, GitHub auth/secret subcommands, and simple rm commands are denied.
- Secret-shaped .env files and .streamlit/secrets.toml are denied by the read tool.
- External-directory tool access is denied.
- The frontierlab-review subagent is read-only: no edits, shell, tool delegation, or external web access.

OpenCode permissions are NOT an OS-level sandbox; an approved shell command, unknown plugin, modified installation, or privileged account can still access sensitive resources. Prefer a throwaway checkout without personal keys. Do not place GitHub secrets or private Nature+ PDFs there. Do not use blanket auto-approve.

## Model choice: optional NVIDIA
OpenCode has a first-party NVIDIA provider integration. Locally use /connect, choose NVIDIA, and connect an API key only on your machine (not in source control, chat, or logs); select a model with /models. Availability, costs, and quota are account-specific. GitHub Actions secrets do not automatically become local OpenCode credentials. No provider or model is selected by the committed configuration.

## Initial exercise
Use Plan or frontierlab-review to review frontierlab/claim_verification.py and tests/test_claim_verification.py. Ask it to distinguish source ID validity, exact passage matching and semantic entailment, then suggest three false-positive regression cases. No file writes until independently reviewed.

## Deployment isolation
The HF Space Dockerfile runs Streamlit only. Adding OpenCode config to the public GitHub repo never starts an OpenCode process or paid inference request. Meta Muse Glimmer NIM still needs one successful manual synthetic-data inference run after the v0.6.1 token-budget fix.
