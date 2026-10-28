"""Zero-network preflight for the optional Llama 3.1 8B baseline."""
from __future__ import annotations
import json

from frontierlab.llama31_baseline import (
    CONTEXT_TOKENS,
    MODEL_ID,
    SUPPORTED_LANGUAGES,
    benchmark_dimensions,
)


def main():
    print(json.dumps({
        "status": "OFFLINE_CONTRACT_PREFLIGHT_ONLY",
        "model": MODEL_ID,
        "model_loaded": False,
        "network_calls": 0,
        "context_tokens": CONTEXT_TOKENS,
        "supported_languages": list(SUPPORTED_LANGUAGES),
        "role": "local general-purpose baseline / worker",
        "benchmark_dimensions": benchmark_dimensions(),
        "boundary": (
            "Llama 3.1 8B is a comparative baseline and optional local worker. "
            "It does not replace Meta Muse Glimmer as the verified research backend "
            "and cannot bypass FrontierLab human review or planning gates."
        ),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
