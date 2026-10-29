# Revision-bound Hugging Face deployment

Target: https://huggingface.co/spaces/Jaycee766/FrontierLab-Meta-Hackathon-2026

The existing public Docker Space uses CPU Basic. `scripts/deploy_hf_space.py` checks the owner, target, visibility, SDK and current/requested hardware before updating it. It does not create a replacement Space or change hardware.

The manual `Deploy FrontierLab to existing HF Space` workflow runs software tests before using the existing GitHub `HF_TOKEN1` secret for the Hub commit. The deployment credential is used only in the deployment runner; it is not included in uploaded files, container layers or Space configuration. No NVIDIA credential or inference opt-in is transferred.

The public app, Python modules, excerpt dataset and documentation are uploaded from the checked-out source revision. The Docker image uses those local snapshot files rather than cloning moving `main` during a build. `deployment.json` records the full source SHA and asset hashes; the UI displays the source revision. The Hub commit receipt alone establishes upload, not a running app: verify the runtime SHA, RUNNING status, Streamlit health endpoint and rendered UI after the build.

The v0.16 interface displays the completed two-claim review with Jaycee871's supplied rationales. The original pending review and extraction receipt remain historical records. The separate 12-case pilot has not received human labels. Deployment does not generate hypotheses or approve a research plan.

Verified October 28, 2026 (Asia/Taipei): v0.16 is RUNNING on the intended CPU Basic Space; its runtime SHA matches the upload receipt. The health endpoint returns HTTP 200/ok and the rendered page shows the deployed source marker and both supplied human-review judgments/rationales. HF NIM inference remains owner-disabled. See [deployment receipt](runs/hf_deployment_20261028.json).


## Latest source upload — October 29, 2026

After v0.25 (the provenance-tagged evidence graph) was merged to `main`, the manual deployment workflow [run 40740516474](https://github.com/Jaycee871/FrontierLab-Meta-Hackathon-2026/actions/runs/40740516474) ran the full software suite and reported **289 passing tests**.

The deploy step recorded:

- source SHA: `0adcfb37e11290c30a4649c8b7712419502a4a52`
- previous Space commit: `2636cac719a30a926aaad975338ab75d14234966`
- new Space commit: `429f4accad2d141aadde6c1eaba1224771f90158`
- target: `Jaycee766/FrontierLab-Meta-Hackathon-2026`
- workflow status: `HF_SOURCE_COMMITTED_BUILD_PENDING`

This proves that the exact v0.25 source bundle was committed to the existing Space repository. It does **not**, by itself, prove that the new Docker build finished successfully or that the newer runtime was healthy. The earlier v0.16 runtime/health verification remains valid for that earlier deployed build; a fresh runtime SHA / RUNNING / health / rendered-marker check is still required before claiming the v0.25 Space is independently verified running.

Open PRs #9 and #10 are not part of this uploaded source snapshot.
