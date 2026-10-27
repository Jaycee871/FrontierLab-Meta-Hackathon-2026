# 🦞 FrontierLab × OpenClaw × NVIDIA OpenShell

Status 2026-10-27: offline permission-gate tests written; real OpenShell deployment, policy DENIED event, OpenClaw inference, and GPU use NOT VERIFIED.

## Goal and isolation boundary

FrontierLab holds research authority and human approval. OpenClaw is only an optional, isolated scientific tool executor. It initially receives synthetic fixtures; NO Meta paid API, GitHub/NVIDIA/HF/Kaggle credentials, private research files, repository-write permission, or default external network access may be assumed.

Two approaches exist: (A) whole OpenClaw community image inside an NVIDIA OpenShell sandbox; (B) host OpenClaw Gateway with an OpenShell command-execution backend. Approach B leaves Gateway/host plugins OUTSIDE the sandbox. Start with A to reduce initial trust surface.

## Offline tests (NOT real sandbox evidence)

From repo root:

    python -m pytest -q
    python -m scripts.lobster_guard_demo

The output labels every decision SIMULATED_APPLICATION_GATE_ONLY. This is a code-level allowance test, not an OpenShell network or filesystem denial test. Do not use it as proof of actual kernel-level isolation.

## On an actual OpenShell-capable Linux host

Follow the reviewed NVIDIA installation guide (Docker/Podman or a separately configured remote gateway may be needed):

https://docs.nvidia.com/openshell/latest/about/installation

    python scripts/openshell_preflight.py
    bash scripts/openshell_lobster.sh launch

Launch uses the bundled community OpenClaw image and interactive openclaw-start wizard. It explicitly requires CLI support for --no-auto-providers so existing credentials are not silently attached. If interactive onboarding asks for paid API keys, do not enter them. If the CLI version differs, inspect help; do not disable protections to make it run. This script does not automatically start or purchase GPU instances.

Review actual effective permissions and perform a benign boundary probe:

    bash scripts/openshell_lobster.sh inspect
    bash scripts/openshell_lobster.sh probe
    openshell logs frontierlab-claw --tail

A **real** enforcement result requires:
1. Documented effective network/filesystem policy and provider list (no unexpected credentials).
2. An attempted benign unauthorized request (example.com).
3. A matching OpenShell DENIED policy log entry. A mere curl failure could be DNS/network outage and is INCONCLUSIVE.
4. No direct host repository or secret mounts; filesystem test only with disposable canaries and independent proof of policy enforcement.

If the request succeeds, treat the expected deny policy as FAILED, and stop further execution. The OpenClaw community image may bundle its own policy, and attached providers can broaden the effective policy; never assume the empty-default OpenShell policy automatically applies.

When finished:

    bash scripts/openshell_lobster.sh cleanup

## Research and competition constraints

Future FrontierLab integration should copy approved synthetic task packets into the sandbox, export output through a reviewed channel, and verify source IDs/conflict/audit data and human approval outside the agent. Do not let OpenClaw push to GitHub autonomously. OpenClaw/OpenShell alone DO NOT meet the hackathon's requirement to use an actual Meta model. A real Meta open-weight inference path remains a separate milestone; Meta billed Model API remains disabled.

Official documentation:
- https://docs.openclaw.ai/gateway/openshell
- https://docs.nvidia.com/openshell/dev/how-it-works/policies/overview
- https://build.nvidia.com/station/openshell/instructions
