"""Offline preflight for the Muse Spark Open hosted-backend contract.

No provider request is made and no credential is read.
"""
from __future__ import annotations
import json

from frontierlab.muse_spark_open import (
    CANONICAL_MODEL,
    MAX_CONTEXT_TOKENS,
    PROVIDERS,
    build_request_content,
)


def main():
    media = [
        {"type": "image", "source": "demo://structure-figure", "mime_type": "image/png"},
        {"type": "video", "source": "demo://assay-video", "mime_type": "video/mp4"},
    ]
    packet = {
        "status": "OFFLINE_CONTRACT_PREFLIGHT_ONLY",
        "canonical_model": CANONICAL_MODEL,
        "context_window": MAX_CONTEXT_TOKENS,
        "official_hosted_model_strings": PROVIDERS,
        "example_content_types": [x["type"] for x in build_request_content(
            "Inspect evidence conservatively.", media
        )],
        "network_calls": 0,
        "credentials_read": 0,
        "boundary": (
            "FrontierLab defines a provider-neutral Muse Spark contract only. "
            "No hosted provider is called until an explicitly authorized transport is supplied."
        ),
    }
    print(json.dumps(packet, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
