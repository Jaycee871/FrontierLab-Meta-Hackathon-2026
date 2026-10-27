# FrontierLab v0.11 — Research Failure Lab

**STATUS: OFFLINE, HAND-AUTHORED POLICY CHECKS ONLY.** No actual Meta inference, scientific model evaluation, human-participant study, or biological discovery has happened.

## Four-paper research basis (user-supplied literature)

- Kong et al., AI for Auto-Research: Roadmap & User Guide, arXiv:2605.18661v2 (2026): integrity across the Creation→Writing→Validation→Dissemination lifecycle; records must survive handoffs, with transparent source versioning and failures.
- Schut et al., Bridging the Human–AI Knowledge Gap: Concept Discovery and Transfer in AlphaZero, arXiv:2310.16410 (2023): the paper explored machine-unique chess concepts and evaluated concept transfer with four grandmasters. Mere before/after correlation cannot by itself prove causal knowledge transfer.
- Zhu et al., Machine learning dataset and benchmark for accurate T cell receptor–pHLA binding prediction, Nature Computational Science DOI 10.1038/s43588-026-01073-y (2026): peptide-disjoint unseen evaluation and negative-data sampling matter. Our guard verifies exact split group identifiers ONLY, not bias-free negatives or OOD generalization.
- Miao et al., Reimagining research papers as interactive and reliable AI agents, Nature DOI 10.1038/s41586-026-11044-y (2026): reproducibility requires verified original methods, code, inputs and outputs—not merely an executable program. Our BioNeMo JSON shape checker is NOT an external proof of model execution.

## v0.11 mechanisms

### 1. Source-version-bound human annotations

Every v0.9 review case is now tied to a SHA256 fingerprint of the selected paper ID, title, year, authors, abstract, URL, DOI, source and synthetic flag. The reviewer dataset hash binds the research question as well. If any underlying record changes, old manual approvals are invalidated. This protects against accidental stale approvals; the reviewer is still a user, not a cryptographically authenticated independent expert.

### 2. Four deterministic failure checks

Evidence → Hypothesis: checks paper ID, cited verbatim quote and version, plus reviewer disposition. Passing returns PASS_HUMAN_REVIEWED_ONLY, NEVER a claim of scientific truth or independent semantic entailment.

Tool → Research Claim: the v0.10 offline Boltz2 preflight and shape-only output cannot be promoted to authenticated scientific model execution. A claimed SUCCESS field or convincing confidence_scores is insufficient. Live origin verification is intentionally not implemented in v0.11.

Dataset → Evaluation: train/test/unseen peptide group IDs must be disjoint. This fails to detect homologous contamination, sample selection artifacts and label bias and does not validate any immunology model.

Machine Concept → Human: paired before/after human scores must come from a documented intervention using held-out problems; output is labelled DESCRIPTIVE_ONLY_NO_CAUSAL_CLAIM. No real participant scores exist here.

### 3. Synthetic stress test pack

12 deliberately fictional scenarios: missing reviewer, wrong citation, invented quote, changed abstract, human rejected a claim, human accepted a still-unverified interpretation, spoofed NIM response, tool error, peptide overlap, disjoint peptide groups, missing held-out human test and purely descriptive human pre/post observations.

All examples and expected labels were authored for exercising deterministic code. 12/12 only means software decisions match handcrafted expectations, not Meta model accuracy, scientific correctness or genuine concept transfer.

## Run without keys or GPU

    python -m scripts.research_failure_lab
    python -m pytest -q

Streamlit synthetic demo includes a collapsible Research Failure Lab and downloadable fictional JSON. Updated UI is not automatically deployed by GitHub commits: rebuilding the HF Space from main is a separate task.

## Required steps for genuine future evaluation

1. Curate legally reusable papers and independently annotated claim-to-excerpt negative examples; record specific article revisions and citation provenance.
2. Run authentic Meta model inference on preregistered tasks; log real raw response and failures, budget, model identity, and controlled baselines.
3. Verify executable science with trusted runtime records, original method/code versions and independent published reference artifacts.
4. Perform held-out evaluation with contamination and negative sampling checks, uncertainty and independent review. For human knowledge transfer, use human participants and a separately planned study rather than fabricated scores.

## Safety & data boundaries

Nothing in this commit sends data to NVIDIA, Meta, Nature or any other hosted inference service. Uploaded copyrighted PDFs are referenced only as research background; their full text is not uploaded into GitHub. No paid API key or HF Space hardware change is required.
