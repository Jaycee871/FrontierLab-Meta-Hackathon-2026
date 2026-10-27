"""Invented, unmistakably synthetic cases for testing conflict/audit behavior."""
from .models import Paper

QUESTION = "How might pH-dependent protein binder affinity be evaluated reproducibly?"
QUERY = '(pH dependent antibody binding) AND (histidine OR engineering)'

DEMO_PAPERS = [
    Paper(
        paper_id="SYNTHETIC:A", title="[FICTIONAL] Histidine substitution pilot A",
        year="2026", authors="Synthetic case A", abstract="Invented test result: a histidine variant improves target binding at acidic pH under one buffer condition, but no replication was conducted.",
        url="", source="Synthetic fixture", synthetic=True,
    ),
    Paper(
        paper_id="SYNTHETIC:B", title="[FICTIONAL] Histidine substitution pilot B",
        year="2026", authors="Synthetic case B", abstract="Invented test result: the same substitution reduces affinity at acidic pH under a different ionic-strength condition. Small hypothetical sample.",
        url="", source="Synthetic fixture", synthetic=True,
    ),
    Paper(
        paper_id="SYNTHETIC:C", title="[FICTIONAL] Assay reliability audit",
        year="2026", authors="Synthetic case C", abstract="Invented study: independent repeats showed buffer and assay format could change the direction of observed pH effects.",
        url="", source="Synthetic fixture", synthetic=True,
    ),
]

DEMO_CLAIMS = [
    {"paper_id": "SYNTHETIC:A", "claim_key": "histidine-acidic-ph-affinity", "stance": "supports", "statement": "Synthetic case A reports an increase under a single buffer condition.", "limitation": "No independent replication."},
    {"paper_id": "SYNTHETIC:B", "claim_key": "histidine-acidic-ph-affinity", "stance": "contradicts", "statement": "Synthetic case B reports a decrease under different ionic strength.", "limitation": "Assay conditions differ; small hypothetical sample."},
    {"paper_id": "SYNTHETIC:C", "claim_key": "assay-condition-sensitivity", "stance": "mixed", "statement": "Synthetic case C reports assay-condition effects.", "limitation": "Invented source only; cannot generalize."},
]
