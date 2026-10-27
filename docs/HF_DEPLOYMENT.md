# Revision-bound Hugging Face deployment

Target: https://huggingface.co/spaces/Jaycee766/FrontierLab-Meta-Hackathon-2026

The existing public Docker Space uses CPU Basic. `scripts/deploy_hf_space.py` checks the owner, target, visibility, SDK and current/requested hardware before updating it. It does not create a replacement Space or change hardware.

The manual `Deploy FrontierLab to existing HF Space` workflow runs software tests before using the existing GitHub `HF_TOKEN1` secret for the Hub commit. The deployment credential is used only in the deployment runner; it is not included in uploaded files, container layers or Space configuration. No NVIDIA credential or inference opt-in is transferred.

The public app, Python modules, excerpt dataset and documentation are uploaded from the checked-out source revision. The Docker image uses those local snapshot files rather than cloning moving `main` during a build. `deployment.json` records the full source SHA and asset hashes; the UI displays the source revision. The Hub commit receipt alone establishes upload, not a running app: verify the runtime SHA, RUNNING status, Streamlit health endpoint and rendered UI after the build.

The v0.16 interface displays the completed two-claim review with Jaycee871's supplied rationales. The original pending review and extraction receipt remain historical records. The separate 12-case pilot has not received human labels. Deployment does not generate hypotheses or approve a research plan.
