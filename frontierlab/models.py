"""Typed data contracts and strict, transparent validation."""
from __future__ import annotations
from dataclasses import asdict, dataclass, field
from typing import Literal

Stance = Literal["supports", "contradicts", "mixed", "inconclusive"]

@dataclass(frozen=True)
class Paper:
    paper_id: str
    title: str
    year: str
    authors: str
    abstract: str
    url: str
    doi: str = ""
    source: str = "Europe PMC"
    synthetic: bool = False

@dataclass(frozen=True)
class Claim:
    paper_id: str
    claim_key: str
    stance: Stance
    statement: str
    limitation: str
    evidence_quote: str = ""
    passage_matched: bool = False

@dataclass
class Audit:
    verified_claims: list[Claim] = field(default_factory=list)
    rejected_claims: list[dict] = field(default_factory=list)
    conflicts: list[dict] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return asdict(self)

@dataclass
class Run:
    question: str
    mode: str
    model: str
    papers: list[Paper]
    audit: Audit
    hypotheses: list[dict]
    skeptic: dict
    log: list[dict]
    plan: dict | None = None
    review: dict | None = None
    evaluation: dict | None = None
    backend: str = "none"
    inference: dict | None = None
    evidence_graph: dict | None = None
    human_events: list[dict] = field(default_factory=list)

    def as_dict(self) -> dict:
        return asdict(self)

