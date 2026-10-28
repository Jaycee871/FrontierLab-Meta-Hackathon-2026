import json
import pytest

from frontierlab.muse_spark_open import (
    CANONICAL_MODEL,
    MuseSparkHostedClient,
    SparkCallBudget,
    build_request_content,
    provider_config,
    provider_model,
)


class FakeTransport:
    def __init__(self, *, model="meta-models/Muse-Spark-Open-816B-A42B", finish_reason="stop"):
        self.model = model
        self.finish_reason = finish_reason
        self.calls = []

    def complete(self, **kwargs):
        self.calls.append(kwargs)
        return {
            "model": self.model,
            "content": json.dumps({"hypotheses": [{"text": "bounded result"}]}),
            "usage": {"prompt_tokens": 100, "completion_tokens": 25, "total_tokens": 125},
            "finish_reason": self.finish_reason,
        }


def test_official_provider_model_strings_and_modalities_are_explicit():
    assert provider_model("together") == "meta-models/Muse-Spark-Open-816B-A42B"
    assert provider_model("together-promo") == "meta-models/muse-spark-open-816b-promo"
    assert provider_model("fireworks") == "accounts/fireworks/models/muse-spark-open"
    assert provider_config("together")["media"] == {"image", "audio", "video"}
    assert provider_config("fireworks")["media"] == {"image"}
    assert provider_config("together-promo")["temporary_promo"] is True
    with pytest.raises(ValueError, match="Unsupported"):
        provider_model("unknown")


def test_text_research_client_matches_existing_json_contract():
    transport = FakeTransport()
    client = MuseSparkHostedClient(
        provider="together",
        transport=transport,
        authorized=True,
        budget=SparkCallBudget(limit=2),
    )
    out = client.json("Hypothesis Agent", "Propose one bounded hypothesis.", {"source": "P1"})
    assert out["hypotheses"][0]["text"] == "bounded result"
    assert client.backend == "muse-spark-together"
    assert client.model == "meta-models/Muse-Spark-Open-816B-A42B"
    assert client.canonical_model == CANONICAL_MODEL
    assert client.provenance["attempted_calls"] == 1
    receipt = client.provenance["receipts"][0]
    assert receipt["media_types"] == []
    assert receipt["status"] == "JSON_OBJECT_RETURNED"
    assert len(receipt["input_sha256"]) == 64
    assert len(receipt["output_sha256"]) == 64
    assert transport.calls[0]["max_tokens"] == 4096


def test_multimodal_call_accepts_image_audio_video_without_logging_raw_media():
    transport = FakeTransport()
    client = MuseSparkHostedClient(
        provider="together", transport=transport, authorized=True
    )
    out = client.multimodal_json(
        "Multimodal Evidence Agent",
        "Inspect the supplied scientific evidence without inventing measurements.",
        {"claim": "pH selectivity increased"},
        media=[
            {"type": "image", "source": "opaque-image-ref", "mime_type": "image/png"},
            {"type": "audio", "source": "opaque-audio-ref", "mime_type": "audio/wav"},
            {"type": "video", "source": "opaque-video-ref", "mime_type": "video/mp4"},
        ],
    )
    assert "hypotheses" in out
    receipt = client.provenance["receipts"][0]
    assert receipt["media_types"] == ["image", "audio", "video"]
    assert "opaque-image-ref" not in json.dumps(receipt)
    blocks = transport.calls[0]["content"]
    assert [block["type"] for block in blocks] == ["text", "image", "audio", "video"]



def test_fireworks_serverless_allows_image_but_blocks_unadvertised_audio_video():
    image_transport = FakeTransport(model="accounts/fireworks/models/muse-spark-open")
    client = MuseSparkHostedClient(
        provider="fireworks", transport=image_transport, authorized=True
    )
    client.multimodal_json(
        "Multimodal Evidence Agent",
        "Inspect image evidence.",
        {"claim": "bounded"},
        media=[{"type": "image", "source": "opaque-image-ref", "mime_type": "image/png"}],
    )
    assert client.provenance["receipts"][0]["media_types"] == ["image"]

    blocked_transport = FakeTransport(model="accounts/fireworks/models/muse-spark-open")
    blocked = MuseSparkHostedClient(
        provider="fireworks", transport=blocked_transport, authorized=True
    )
    with pytest.raises(ValueError, match="does not advertise"):
        blocked.multimodal_json(
            "Multimodal Evidence Agent",
            "Inspect audio evidence.",
            {"claim": "bounded"},
            media=[{"type": "audio", "source": "opaque-audio-ref", "mime_type": "audio/wav"}],
        )
    assert blocked.provenance["attempted_calls"] == 0
    assert blocked_transport.calls == []


def test_request_content_rejects_unbounded_or_unknown_media():
    with pytest.raises(ValueError, match="Unsupported"):
        build_request_content("x", [{"type": "pdf", "source": "x"}])
    with pytest.raises(ValueError, match="eight"):
        build_request_content("x", [{"type": "image", "source": str(i)} for i in range(9)])


def test_call_budget_and_no_automatic_retry():
    transport = FakeTransport()
    client = MuseSparkHostedClient(
        provider="together",
        transport=transport,
        authorized=True,
        budget=SparkCallBudget(limit=1),
    )
    client.json("Hypothesis Agent", "one", {})
    with pytest.raises(PermissionError, match="budget exhausted"):
        client.json("Hypothesis Agent", "two", {})
    assert len(transport.calls) == 1


def test_failed_model_identity_is_redacted_and_not_retried():
    transport = FakeTransport(model="some-other-model")
    client = MuseSparkHostedClient(
        provider="together",
        transport=transport,
        authorized=True,
        budget=SparkCallBudget(limit=2),
    )
    with pytest.raises(RuntimeError, match="no automatic retry"):
        client.json("Hypothesis Agent", "x", {})
    assert len(transport.calls) == 1
    assert client.provenance["receipts"][0]["status"] == "FAILED_NO_RETRY"


def test_explicit_authorization_and_transport_are_required():
    with pytest.raises(PermissionError, match="authorization"):
        MuseSparkHostedClient(provider="together", transport=FakeTransport())
    with pytest.raises(TypeError, match="complete"):
        MuseSparkHostedClient(provider="together", transport=object(), authorized=True)
