"""BioNeMo sidecar never invokes a remote endpoint in automated tests."""
import json
import pytest
from frontierlab.bionemo import (
    BOLTZ2_URL, registry, prepare_boltz2, validate_boltz2_response,
)
from frontierlab.models import Paper
from frontierlab.pipeline import run_research
from frontierlab.review import review_packet, save_review

SEQUENCE = "ACDEFGHIKLMNPQRSTVWYACDEFGHIKLMNPQRSTVWY"

def test_registry_names_and_honest_status():
    names = {t["name"]:t["stage"] for t in registry()}
    assert names["boltz2-nim"] == "OFFLINE_PREFLIGHT_ONLY"
    assert names["proteinmpnn-nim"] == "NOT_CONNECTED"
    assert names["rfdiffusion-nim"] == "NOT_CONNECTED"
    assert names["openfold3-nim"] == "NOT_CONNECTED"

def test_offline_preflight_is_stable_redacted_and_zero_network():
    a = prepare_boltz2(SEQUENCE, source_id="PUBLIC:fixture-1")
    b = prepare_boltz2(SEQUENCE, source_id="PUBLIC:fixture-1")
    assert a.manifest == b.manifest
    assert a.manifest["status"] == "PREPARED_NOT_EXECUTED"
    assert a.manifest["network_invocation_occurred"] is False
    assert a.manifest["endpoint_reference"] == BOLTZ2_URL
    assert SEQUENCE not in json.dumps(a.manifest)
    assert a.request["polymers"][0]["sequence"] == SEQUENCE

@pytest.mark.parametrize("sequence", ["", "SHORT", "AA AAAAAAA", "acdefghik", "ACD3GHIK", "A"*4097])
def test_rejects_invalid_protein_inputs(sequence):
    with pytest.raises(ValueError):
        prepare_boltz2(sequence, source_id="PUBLIC:fixture")

@pytest.mark.parametrize("settings", [
    {"recycling_steps":0}, {"recycling_steps":True},
    {"sampling_steps":9}, {"sampling_steps":1001},
    {"diffusion_samples":0}, {"diffusion_samples":26},
])
def test_rejects_unsupported_parameters(settings):
    with pytest.raises(ValueError):
        prepare_boltz2(SEQUENCE, source_id="PUBLIC:fixture", **settings)

def test_research_preflight_requires_human_gate():
    with pytest.raises(PermissionError):
        prepare_boltz2(SEQUENCE, source_id="PUBLIC:example", mode="research")
    with pytest.raises(ValueError):
        prepare_boltz2(SEQUENCE, source_id="PUBLIC:example",
                       mode="offline_fixture", researcher_authorized=True)

def test_response_shape_checks_without_live_identity_claim():
    p = prepare_boltz2(SEQUENCE, source_id="PUBLIC:test")
    answer = {
        "structures": [{"structure": "data_model\\n_atom_site.id\\n1\\n", "format": "mmcif"}],
        "confidence_scores": [0.87],
        "metrics": {"elapsed_ms": 100},
    }
    checked = validate_boltz2_response(p, answer)
    assert checked["status"] == "RESPONSE_SHAPE_CHECKED_ORIGIN_UNVERIFIED"
    assert checked["structure_count"] == 1
    assert checked["confidence_scores"] == [0.87]
    assert checked["source_response_validated_as_live"] is False
    assert checked["biological_activity_confirmed"] is False
    assert SEQUENCE not in json.dumps(checked)

@pytest.mark.parametrize("invalid", [
    {},
    {"structures": [], "confidence_scores": []},
    {"structures": [{"structure": "ABC", "format":"pdb"}], "confidence_scores":[0.8]},
    {"structures": [{"structure": "", "format":"mmcif"}], "confidence_scores":[0.8]},
    {"structures": [{"structure": "data_x", "format":"mmcif"}], "confidence_scores":[float("nan")]},
    {"structures": [{"structure": "data_x", "format":"mmcif"}], "confidence_scores":[True]},
])
def test_response_rejects_missing_or_invalid_fields(invalid):
    p = prepare_boltz2(SEQUENCE, source_id="PUBLIC:test")
    with pytest.raises((ValueError, TypeError)):
        validate_boltz2_response(p, invalid)

def test_non_reviewed_research_cannot_prepare_bionemo():
    p1=Paper("PMID:1","Paper One","2026","A",
             "The experimental assay showed a dependence on buffer conditions.",
             "https://example.org/1")
    p2=Paper("PMID:2","Paper Two","2026","A",
             "The experimental assay showed a dependence on buffer conditions.",
             "https://example.org/2")
    class Mock:
        model = "mock-not-meta"
        def json(self, role, task, payload):
            if role=="Evidence Extraction Agent":
                return {"claims": [{"paper_id":payload["paper"]["paper_id"],
                         "claim_key":"assay","stance":"supports",
                         "statement":"Assay conditions matter",
                         "limitation":"Abstract only",
                         "evidence_quote":"The experimental assay showed a dependence on buffer conditions."}]}
            raise AssertionError("No skeptic or hypothesis calls before review")
    run=run_research("Review assay", "query", mode="live",
                     model_client=Mock(), retrieve=lambda q,n:[p1,p2])
    with pytest.raises(PermissionError):
        prepare_boltz2(SEQUENCE, source_id="PUBLIC:test", mode="research",
                       run=run, researcher_authorized=True)
    cases=review_packet(run)["cases"]
    save_review(run,[{"case_id":c["case_id"], "review_label":"SUPPORTED"} for c in cases])
    accepted=prepare_boltz2(SEQUENCE, source_id="PUBLIC:test", mode="research",
                            run=run, researcher_authorized=True)
    assert accepted.manifest["human_supported_evidence_ids"] == ["PMID:1","PMID:2"]
    assert accepted.manifest["network_invocation_occurred"] is False
