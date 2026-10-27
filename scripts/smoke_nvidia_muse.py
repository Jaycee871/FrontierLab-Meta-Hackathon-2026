"""Single opt-in fictional-data call to NVIDIA trial model; no automatic retry."""
from datetime import datetime, timezone
import hashlib
import json
import os
import re
import time

from frontierlab.nvidia_muse import NvidiaMuseClient, MODEL

PROMPT = (
    "FICTIONAL DATA ONLY. Study A reports increased binding in buffer X. "
    "Study B reports decreased binding in buffer Y. "
    "In one short sentence, say whether these two studies justify a universal "
    "claim that the intervention always increases binding. Mention uncertainty."
)


def _run_context():
    """Only allow public, structured CI identifiers into the receipt."""
    sha = os.getenv("GITHUB_SHA", "")
    run_id = os.getenv("GITHUB_RUN_ID", "")
    attempt = os.getenv("GITHUB_RUN_ATTEMPT", "")
    return {
        "git_sha": sha if re.fullmatch(r"[0-9a-fA-F]{40}", sha) else None,
        "github_run_id": run_id if run_id.isascii() and run_id.isdigit() else None,
        "github_run_attempt": attempt if attempt.isascii() and attempt.isdigit() else None,
    }


def main():
    if os.getenv("FRONTIERLAB_NVIDIA_TRIAL") != "YES":
        print("TRIAL_NOT_AUTHORIZED: no call made")
        return 2

    started = time.perf_counter()
    receipt = {
        "schema_version": 1,
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        **_run_context(),
        "requested_model": MODEL,
        "max_tokens": 2048,
        "reasoning_effort": "low",
        "synthetic_input_only": True,
        "input_sha256": hashlib.sha256(PROMPT.encode("utf-8")).hexdigest(),
        "paid_meta_platforms_api_used": False,
    }
    try:
        result = NvidiaMuseClient().complete(PROMPT, max_tokens=2048)
    except (RuntimeError, ValueError, PermissionError) as exc:
        # Do not publish arbitrary exception text, request headers or response bodies.
        receipt.update(status="NIM_CHECK_FAILED", error_type=type(exc).__name__,
                       elapsed_seconds=round(time.perf_counter() - started, 3))
        print(json.dumps(receipt, ensure_ascii=False, indent=2))
        return 1

    answer = result["content"]
    finished = result["finish_reason"] == "stop"
    identified = isinstance(result["model"], str) and "muse-glimmer" in result["model"].lower()
    status = ("REAL_INFERENCE_RETURNED" if finished and identified else
              "INCOMPLETE_FINAL_ANSWER" if not finished else "MODEL_IDENTITY_UNVERIFIED")
    receipt.update({
        "status": status,
        "reported_model": result["model"],
        "finish_reason": result["finish_reason"],
        "elapsed_seconds": round(time.perf_counter() - started, 3),
        "output_sha256": hashlib.sha256(answer.encode("utf-8")).hexdigest(),
        "output_excerpt": answer[:350],
        "usage": result["usage"],
    })
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0 if status == "REAL_INFERENCE_RETURNED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
