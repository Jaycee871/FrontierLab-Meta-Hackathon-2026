"""Offline-first NVIDIA BioNeMo scientific-tool adapter.

Only implements *preparation* and *response checking* for Boltz-2 NIM.
NO HTTP client, API key handling, Docker launch, or GPU execution here.
Never mistake schema validation for biological confirmation.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass
from typing import Any

from .models import Run

BIONEMO_REPO = "https://github.com/NVIDIA-BioNeMo/bionemo-agent-toolkit"
BOLTZ2_URL = "https://health.api.nvidia.com/v1/biology/mit/boltz2/predict"
SCHEMA = "frontierlab.bionemo.preflight.v1"
AA = frozenset("ACDEFGHIKLMNPQRSTVWY")

SKILLS = (
    {"name": "boltz2-nim", "task": "biomolecular structure prediction",
     "stage": "OFFLINE_PREFLIGHT_ONLY",
     "source": BIONEMO_REPO + "/tree/main/nim-skills/boltz2-nim"},
    {"name": "proteinmpnn-nim", "task": "sequence design for a known backbone",
     "stage": "NOT_CONNECTED",
     "source": BIONEMO_REPO + "/tree/main/nim-skills/proteinmpnn-nim"},
    {"name": "rfdiffusion-nim", "task": "protein backbone generation",
     "stage": "NOT_CONNECTED",
     "source": BIONEMO_REPO + "/tree/main/nim-skills/rfdiffusion-nim"},
    {"name": "openfold3-nim", "task": "biomolecular structure prediction",
     "stage": "NOT_CONNECTED",
     "source": BIONEMO_REPO + "/tree/main/nim-skills/openfold3-nim"},
)

def registry() -> list[dict[str, str]]:
    """Tool availability is explicit; no endpoint is called or probed."""
    return [dict(tool) for tool in SKILLS]


def _canonical(payload: Any) -> bytes:
    return json.dumps(payload, ensure_ascii=True, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _validate_sequence(sequence: str) -> str:
    if not isinstance(sequence, str) or not 8 <= len(sequence) <= 4096:
        raise ValueError("Protein sequence must have 8–4096 residues")
    if any(residue not in AA for residue in sequence):
        raise ValueError("Only uppercase canonical 20-residue protein sequences are supported")
    return sequence


def _validate_id(source_id: str) -> str:
    if not isinstance(source_id, str) or not re.fullmatch(r"[A-Za-z0-9:._/-]{3,160}", source_id):
        raise ValueError("Source ID must be a nonempty plain identifier")
    return source_id


@dataclass(frozen=True)
class Boltz2Preflight:
    """Internal request contains the sequence. Publish .manifest only after review."""
    request: dict[str, Any]
    manifest: dict[str, Any]


def _approved_research(run: Run) -> list[str]:
    from .review import approved_claims, review_packet
    if run.mode != "live":
        raise PermissionError("Only live literature runs can authorize research preflight")
    if not isinstance(run.review, dict) or run.review.get("dataset_id") != review_packet(run)["dataset_id"]:
        raise PermissionError("A valid, source-bound human review is required")
    if run.review.get("status") != "READY_FOR_HUMAN_GATED_SYNTHESIS":
        raise PermissionError("All claims need human review and two distinct supporting sources")
    sources = sorted({c.paper_id for c in approved_claims(run)})
    if len(sources) < 2:
        raise PermissionError("At least two distinct human-supported evidence sources required")
    return sources


def prepare_boltz2(
    sequence: str,
    *,
    source_id: str,
    mode: str = "offline_fixture",
    run: Run | None = None,
    researcher_authorized: bool = False,
    recycling_steps: int = 3,
    sampling_steps: int = 50,
    diffusion_samples: int = 1,
) -> Boltz2Preflight:
    """Build a standard protein-only Boltz2 request, without executing it.

    The offline fixture mode is for inert code tests and exploration. A research
    preflight requires a completed human review and separate explicit consent.
    Neither mode authorizes remote submission of the sequence.
    """
    seq = _validate_sequence(sequence)
    sid = _validate_id(source_id)
    if type(recycling_steps) is not int or not 1 <= recycling_steps <= 10:
        raise ValueError("recycling_steps must be an integer from 1 to 10")
    if type(sampling_steps) is not int or not 10 <= sampling_steps <= 1000:
        raise ValueError("sampling_steps must be an integer from 10 to 1000")
    if type(diffusion_samples) is not int or not 1 <= diffusion_samples <= 25:
        raise ValueError("diffusion_samples must be an integer from 1 to 25")

    if mode == "offline_fixture":
        if run is not None or researcher_authorized:
            raise ValueError("Offline fixtures cannot carry research approvals or runs")
        approved_sources: list[str] = []
    elif mode == "research":
        if run is None or not researcher_authorized:
            raise PermissionError("Real research preflight requires a reviewed run and explicit authorization")
        approved_sources = _approved_research(run)
    else:
        raise ValueError("Unsupported BioNeMo preflight mode")

    request = {
        "polymers": [{"id": "A", "molecule_type": "protein", "sequence": seq}],
        "recycling_steps": recycling_steps,
        "sampling_steps": sampling_steps,
        "diffusion_samples": diffusion_samples,
        "step_scale": 1.638,
        "output_format": "mmcif",
    }
    req_hash = _sha256(_canonical(request))
    manifest = {
        "schema": SCHEMA,
        "status": "PREPARED_NOT_EXECUTED",
        "tool": "boltz2-nim",
        "model": "NVIDIA-hosted Boltz-2 NIM (not called)",
        "endpoint_reference": BOLTZ2_URL,
        "input_source_id": sid,
        "input_sequence_sha256": _sha256(seq.encode("ascii")),
        "input_sequence_length": len(seq),
        "request_sha256": req_hash,
        "request_settings": {
            "recycling_steps": recycling_steps,
            "sampling_steps": sampling_steps,
            "diffusion_samples": diffusion_samples,
            "output_format": "mmcif",
        },
        "mode": mode,
        "researcher_preflight_authorized": researcher_authorized,
        "human_supported_evidence_ids": approved_sources,
        "network_invocation_occurred": False,
        "biological_activity_confirmed": False,
        "scientific_interpretation": "NO MODEL RESULT. This is a schema preflight, not a prediction.",
        "source_skill_url": SKILLS[0]["source"],
    }
    return Boltz2Preflight(request=request, manifest=manifest)


def validate_boltz2_response(prepared: Boltz2Preflight, response: dict[str, Any]) -> dict[str, Any]:
    """Inspect actual response data, never synthesize or fill missing values.

    A validated response is only a correctly shaped computational prediction.
    Provenance requires an external signed/runtime receipt before 'live'
    attribution; caller must not claim HTTP success from this function.
    """
    if not isinstance(prepared, Boltz2Preflight) or not isinstance(response, dict):
        raise TypeError("Boltz2 response and prepared request required")
    structures = response.get("structures")
    confidence = response.get("confidence_scores")
    expected = prepared.request["diffusion_samples"]
    if not isinstance(structures, list) or len(structures) != expected:
        raise ValueError("Missing or mismatched returned structures")
    if not isinstance(confidence, list) or len(confidence) != expected:
        raise ValueError("Missing or mismatched confidence_scores")
    content_hashes = []
    for structure in structures:
        if not isinstance(structure, dict) or structure.get("format") != "mmcif":
            raise ValueError("Every structure must declare format=mmcif")
        content = structure.get("structure")
        if not isinstance(content, str) or not content.strip():
            raise ValueError("Empty or malformed structure")
        content_hashes.append(_sha256(content.encode("utf-8")))
    for score in confidence:
        if type(score) not in (float, int) or not math.isfinite(score):
            raise ValueError("Nonfinite or nonnumeric model confidence")
    # The unit/range of confidence_scores is API-defined, not assumed here.
    return {
        **prepared.manifest,
        "status": "RESPONSE_SHAPE_CHECKED_ORIGIN_UNVERIFIED",
        "structure_count": expected,
        "structure_sha256": content_hashes,
        "confidence_scores": confidence.copy(),
        "response_sha256": _sha256(_canonical(response)),
        "source_response_validated_as_live": False,
        "scientific_interpretation": (
            "Computational model outputs only; confidence_scores are not automatically "
            "pLDDT or proof of experimental binding, function, or clinical efficacy."
        ),
    }
