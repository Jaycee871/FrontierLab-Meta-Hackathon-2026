"""One synthetic-only Muse Glimmer sample. Manual opt-in and NO retry.

Do not put private/subscription full texts in prompts or CI logs.
"""
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
    if os.environ.get("FRONTIERLAB_NVIDIA_TRIAL") != "YES":
        print("TRIAL_NOT_AUTHORIZED: no API call made")
        return 2
    try:
        client=NvidiaMuseClient()
        response=client.complete(PROMPT,max_tokens=192)
    except (RuntimeError, ValueError, PermissionError) as exc:
        print("NIM_CHECK_FAILED:",str(exc))
        return 1
    text=response["content"]
    print(json.dumps({
        "status":"REAL_INFERENCE_RETURNED",
        "requested_model":MODEL,
        "reported_model":response["model"],
        "synthetic_input_only":True,
        "output_sha256":hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "output_excerpt":text[:350],
        "usage":response["usage"],
        "paid_meta_platforms_api_used":False
    },ensure_ascii=False,indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
