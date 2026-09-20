from dataclasses import dataclass, field


@dataclass
class FootprintCandidate:
    id: str
    pad_ids: list[str]
    signature: str | None
    confidence: float
    orientation_deg: float = 0.0
    evidence: list[str] = field(default_factory=list)
    reference: str | None = None
    boundary_source: str = "geometric_proximity"
    boundary_confidence: float = 0.0
