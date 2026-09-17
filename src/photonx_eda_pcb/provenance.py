from __future__ import annotations
from dataclasses import dataclass, field


@dataclass(frozen=True)
class SourceRef:
    path: str
    line: int | None = None
    raw: str | None = None


@dataclass(frozen=True)
class Evidence:
    kind: str
    detail: str
    confidence: float
    source: SourceRef | None = None

    def __post_init__(self):
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("evidence confidence must be in [0, 1]")


@dataclass
class Provenance:
    sources: list[SourceRef] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)

    def add_source(self, source: SourceRef) -> None:
        if source not in self.sources:
            self.sources.append(source)

    def add_evidence(self, evidence: Evidence) -> None:
        self.evidence.append(evidence)
