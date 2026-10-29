"""Controlled gate-ablation helpers.

Two experiment types are deliberately separated:

1. POST_GENERATION_GATE_ABLATION
   Replays deterministic policy layers on one fixed set of model outputs.
   This costs no new model call and cannot isolate prompting effects.

2. PROMPT_AND_POSTPROCESS_ABLATION
   Compares two model outputs generated from the same fixed cases with different
   task instructions, then applies the deterministic source/quote gate.

Neither experiment treats reviewer labels as independent scientific gold.
"""
from __future__ import annotations

from .claim_verification import LABELS, quote_anchored

SCHEMA = "frontierlab.gate-ablation.v2"
PENDING = "PENDING_REVIEW"
DECISIVE = {"SUPPORTED", "CONTRADICTED"}


def _prediction_map(rows: list[dict], expected_case_ids: set[str]) -> dict[str, dict]:
    if not isinstance(rows, list):
        raise ValueError("Prediction rows must be a list")
    out = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("Prediction rows must be objects")
        cid = str(row.get("case_id", "")).strip()
        label = str(row.get("label", "")).upper()
        if not cid or cid in out:
            raise ValueError("Predictions require distinct nonempty case IDs")
        if label not in LABELS:
            raise ValueError("Unrecognized prediction label")
        out[cid] = row
    if set(out) != expected_case_ids:
        raise ValueError("Predictions must cover the exact fixed case set")
    return out


def _fixed_cases(cases: list[dict]) -> tuple[list[str], dict[str, str]]:
    if not isinstance(cases, list) or not cases:
        raise ValueError("A nonempty fixed case set is required")
    ids, sources = [], {}
    for case in cases:
        if not isinstance(case, dict):
            raise ValueError("Cases must be objects")
        cid = str(case.get("case_id", "")).strip()
        sid = str(case.get("source_id", "")).strip()
        if not cid or not sid or cid in sources:
            raise ValueError("Cases require unique IDs and known source IDs")
        ids.append(cid)
        sources[cid] = sid
    return ids, sources


def _label_map(values: dict | None, known: set[str]) -> dict[str, str]:
    if values is None:
        return {}
    if not isinstance(values, dict):
        raise ValueError("Labels must be a mapping")
    out = {}
    for cid, value in values.items():
        if cid not in known:
            raise ValueError("Label supplied for an unknown case")
        label = str(value).upper()
        if label not in LABELS:
            raise ValueError("Unrecognized label")
        out[cid] = label
    return out


def _summary(outputs: dict[str, str]) -> dict:
    values = list(outputs.values())
    total = len(values)
    decisive = sum(value in DECISIVE for value in values)
    abstained = values.count("INSUFFICIENT")
    pending = values.count(PENDING)
    return {
        "outputs": outputs,
        "decisive": decisive,
        "abstained": abstained,
        "pending_review": pending,
        "decisive_rate": round(decisive / total, 4) if total else None,
        "abstention_rate": round(abstained / total, 4) if total else None,
        "pending_review_rate": round(pending / total, 4) if total else None,
    }


def source_quote_arm(
    cases: list[dict],
    predictions: list[dict],
    source_texts: dict[str, str],
) -> dict:
    case_ids, case_sources = _fixed_cases(cases)
    pred = _prediction_map(predictions, set(case_ids))
    if not isinstance(source_texts, dict):
        raise ValueError("source_texts must be a mapping")

    raw, gated, checks = {}, {}, {}
    for cid in case_ids:
        expected_sid = case_sources[cid]
        row = pred[cid]
        label = str(row["label"]).upper()
        raw[cid] = label

        sid = str(row.get("source_id", "")).strip()
        source_matches = sid == expected_sid and isinstance(source_texts.get(sid), str)
        quote = row.get("evidence_quote", "")
        quote = quote if isinstance(quote, str) else ""
        quote_length_valid = 24 <= len(quote.strip()) <= 500
        anchored = bool(
            source_matches
            and quote_length_valid
            and quote_anchored(source_texts[sid], quote)
        )

        checks[cid] = {
            "expected_source_id": expected_sid,
            "reported_source_id": sid,
            "source_matches_case": source_matches,
            "quote_length": len(quote.strip()),
            "quote_length_valid": quote_length_valid,
            "quote_anchored": anchored,
            "decisive_output_requires_quote": label in DECISIVE,
        }
        # A model abstention remains an abstention. A decisive output survives only
        # when its source ID and quote pass the deterministic gate.
        gated[cid] = label if label == "INSUFFICIENT" or anchored else "INSUFFICIENT"

    return {
        "case_ids": case_ids,
        "raw": raw,
        "gated": gated,
        "anchor_checks": checks,
    }


def apply_reviewer_gate(gated: dict[str, str], reviews: dict | None = None) -> dict:
    reviews = _label_map(reviews, set(gated))
    outputs, required_ids = {}, []
    corrections = 0
    reviewer_abstentions = 0

    for cid, label in gated.items():
        if label in DECISIVE:
            required_ids.append(cid)
            if cid in reviews:
                outputs[cid] = reviews[cid]
                corrections += reviews[cid] != label
                reviewer_abstentions += reviews[cid] == "INSUFFICIENT"
            else:
                outputs[cid] = PENDING
        else:
            outputs[cid] = "INSUFFICIENT"

    result = _summary(outputs)
    completed = sum(cid in reviews for cid in required_ids)
    result.update({
        "reviews_required": len(required_ids),
        "reviews_completed": completed,
        "review_completion_rate": (
            round(completed / len(required_ids), 4) if required_ids else 1.0
        ),
        "review_corrections_to_surviving_decisions": corrections,
        "reviewer_abstentions_from_surviving_decisions": reviewer_abstentions,
    })
    return result


def _gold_metrics(
    outputs: dict[str, str],
    gold: dict[str, str],
    case_ids: list[str],
    *,
    independent_gold_verified: bool,
) -> dict:
    complete_gold = len(gold) == len(case_ids) and all(cid in gold for cid in case_ids)
    complete_outputs = all(outputs.get(cid) in LABELS for cid in case_ids)
    reportable = bool(independent_gold_verified and complete_gold and complete_outputs)
    accuracy = None
    if reportable:
        correct = sum(outputs[cid] == gold[cid] for cid in case_ids)
        accuracy = round(correct / len(case_ids), 4)
    return {
        "reference_complete": complete_gold,
        "independent_gold_verified": bool(independent_gold_verified),
        "final_outputs_complete": complete_outputs,
        "accuracy_reportable": reportable,
        "accuracy": accuracy,
    }


def _reviewer_agreement(outputs: dict[str, str], reviews: dict[str, str], case_ids: list[str]) -> dict:
    # Descriptive agreement only. The same reviewer labels are used in Arm C and are
    # not independent gold.
    compared = [
        cid for cid in case_ids
        if cid in reviews and outputs.get(cid) in LABELS
    ]
    return {
        "cases_compared": len(compared),
        "agreement": (
            round(sum(outputs[cid] == reviews[cid] for cid in compared) / len(compared), 4)
            if compared else None
        ),
        "accuracy_claim_allowed": False,
    }


def _attach_reference_metrics(
    arm: dict,
    *,
    outputs: dict[str, str],
    reviews: dict[str, str],
    gold: dict[str, str],
    case_ids: list[str],
    independent_gold_verified: bool,
) -> None:
    arm["agreement_with_supplied_reviewer"] = _reviewer_agreement(outputs, reviews, case_ids)
    arm["gold_metrics"] = _gold_metrics(
        outputs, gold, case_ids,
        independent_gold_verified=independent_gold_verified,
    )


def compare_post_generation_gates(
    cases: list[dict],
    predictions: list[dict],
    source_texts: dict[str, str],
    *,
    reviews: dict | None = None,
    independent_gold: dict | None = None,
    independent_gold_verified: bool = False,
) -> dict:
    fixed = source_quote_arm(cases, predictions, source_texts)
    case_ids = fixed["case_ids"]
    review_labels = _label_map(reviews, set(case_ids))
    gold = _label_map(independent_gold, set(case_ids))

    arm_a = _summary(fixed["raw"])
    arm_b = _summary(fixed["gated"])
    arm_c = apply_reviewer_gate(fixed["gated"], review_labels)

    _attach_reference_metrics(
        arm_a, outputs=fixed["raw"], reviews=review_labels, gold=gold,
        case_ids=case_ids, independent_gold_verified=independent_gold_verified,
    )
    _attach_reference_metrics(
        arm_b, outputs=fixed["gated"], reviews=review_labels, gold=gold,
        case_ids=case_ids, independent_gold_verified=independent_gold_verified,
    )
    _attach_reference_metrics(
        arm_c, outputs=arm_c["outputs"], reviews=review_labels, gold=gold,
        case_ids=case_ids, independent_gold_verified=independent_gold_verified,
    )

    raw_decisive = arm_a["decisive"]
    gated_decisive = arm_b["decisive"]
    return {
        "schema": SCHEMA,
        "comparison_type": "POST_GENERATION_GATE_ABLATION",
        "prompt_effect_isolated": False,
        "case_count": len(case_ids),
        "case_ids": case_ids,
        "arm_a_fixed_model_outputs": arm_a,
        "arm_b_source_quote_post_gate": arm_b,
        "arm_c_source_quote_plus_human_review": arm_c,
        "anchor_checks": fixed["anchor_checks"],
        "effects": {
            "quote_gate_new_abstentions": arm_b["abstained"] - arm_a["abstained"],
            "quote_gate_decisive_retention_rate": (
                round(gated_decisive / raw_decisive, 4) if raw_decisive else None
            ),
            "review_corrections_to_surviving_decisions": (
                arm_c["review_corrections_to_surviving_decisions"]
            ),
        },
        "review_labels_supplied": bool(review_labels),
        "independent_gold_supplied": bool(gold),
        "independent_gold_complete": len(gold) == len(case_ids),
        "independent_gold_verified": bool(independent_gold_verified),
        "accuracy_reportable": bool(
            independent_gold_verified and len(gold) == len(case_ids)
        ),
        "note": (
            "This replays post-generation policy layers on one fixed prediction set. "
            "Because the recorded model prompt already requested evidence quotes, it "
            "does not isolate the effect of quote-grounded prompting."
        ),
    }


def compare_prompt_arms(
    cases: list[dict],
    raw_predictions: list[dict],
    grounded_predictions: list[dict],
    source_texts: dict[str, str],
    *,
    reviews: dict | None = None,
    independent_gold: dict | None = None,
    independent_gold_verified: bool = False,
) -> dict:
    case_ids, _ = _fixed_cases(cases)
    raw_map = _prediction_map(raw_predictions, set(case_ids))
    fixed = source_quote_arm(cases, grounded_predictions, source_texts)
    review_labels = _label_map(reviews, set(case_ids))
    gold = _label_map(independent_gold, set(case_ids))

    raw_outputs = {cid: str(raw_map[cid]["label"]).upper() for cid in case_ids}
    grounded_pre_gate = fixed["raw"]
    grounded_post_gate = fixed["gated"]

    arm_a = _summary(raw_outputs)
    arm_b = _summary(grounded_post_gate)
    arm_c = apply_reviewer_gate(grounded_post_gate, review_labels)

    _attach_reference_metrics(
        arm_a, outputs=raw_outputs, reviews=review_labels, gold=gold,
        case_ids=case_ids, independent_gold_verified=independent_gold_verified,
    )
    _attach_reference_metrics(
        arm_b, outputs=grounded_post_gate, reviews=review_labels, gold=gold,
        case_ids=case_ids, independent_gold_verified=independent_gold_verified,
    )
    _attach_reference_metrics(
        arm_c, outputs=arm_c["outputs"], reviews=review_labels, gold=gold,
        case_ids=case_ids, independent_gold_verified=independent_gold_verified,
    )

    return {
        "schema": SCHEMA,
        "comparison_type": "PROMPT_AND_POSTPROCESS_ABLATION",
        "prompt_effect_isolated": True,
        "case_count": len(case_ids),
        "case_ids": case_ids,
        "arm_a_no_quote_requirement": arm_a,
        "arm_b_quote_grounded_plus_source_quote_gate": arm_b,
        "arm_c_quote_gate_plus_human_review": arm_c,
        "grounded_prompt_outputs_before_post_gate": _summary(grounded_pre_gate),
        "anchor_checks": fixed["anchor_checks"],
        "effects": {
            "prompt_label_changes": sum(
                raw_outputs[cid] != grounded_pre_gate[cid] for cid in case_ids
            ),
            "quote_gate_new_abstentions_after_grounded_prompt": (
                _summary(grounded_post_gate)["abstained"]
                - _summary(grounded_pre_gate)["abstained"]
            ),
            "arm_a_to_arm_b_output_changes": sum(
                raw_outputs[cid] != grounded_post_gate[cid] for cid in case_ids
            ),
            "review_corrections_to_surviving_decisions": (
                arm_c["review_corrections_to_surviving_decisions"]
            ),
        },
        "review_labels_supplied": bool(review_labels),
        "independent_gold_supplied": bool(gold),
        "independent_gold_complete": len(gold) == len(case_ids),
        "independent_gold_verified": bool(independent_gold_verified),
        "accuracy_reportable": bool(
            independent_gold_verified and len(gold) == len(case_ids)
        ),
        "note": (
            "Arm A and Arm B must be generated with the same model and exact case/source "
            "payload. Only the task instruction differs. Reviewer agreement is descriptive "
            "unless a separate independently verified gold set is supplied."
        ),
    }


# Backwards-compatible short name for the offline replay experiment.
compare_gates = compare_post_generation_gates
