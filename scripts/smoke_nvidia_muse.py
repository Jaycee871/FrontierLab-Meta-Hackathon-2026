"""Single opt-in fictional-data call to NVIDIA trial model; no automatic retry."""
import hashlib
import json
import os
from frontierlab.nvidia_muse import NvidiaMuseClient, MODEL

PROMPT = (
    "FICTIONAL DATA ONLY. Study A reports increased binding in buffer X. "
    "Study B reports decreased binding in buffer Y. "
    "In one short sentence, say whether these two studies justify a universal "
    "claim that the intervention always increases binding. Mention uncertainty."
)

def main():
    if os.getenv("FRONTIERLAB_NVIDIA_TRIAL") != "YES":
        print("TRIAL_NOT_AUTHORIZED: no call made")
        return 2
    try:
        result = NvidiaMuseClient().complete(PROMPT, max_tokens=2048)
    except (RuntimeError, ValueError, PermissionError) as exc:
        print("NIM_CHECK_FAILED:", str(exc))
        return 1
    answer = result["content"]
    print(json.dumps({
        "status": "REAL_INFERENCE_RETURNED",
        "requested_model": MODEL,
        "reported_model": result["model"],
        "finish_reason": result["finish_reason"],
        "synthetic_input_only": True,
        "output_sha256": hashlib.sha256(answer.encode("utf-8")).hexdigest(),
        "output_excerpt": answer[:350],
        "usage": result["usage"],
        "paid_meta_platforms_api_used": False,
    }, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
