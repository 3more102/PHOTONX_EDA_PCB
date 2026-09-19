from dataclasses import dataclass, field


@dataclass
class TestPointCandidate:
    # Pytest treats imported classes whose names begin with ``Test`` as test
    # containers.  This is a production data model, so opt it out explicitly
    # without renaming the public API.
    __test__ = False

    object_id: str
    net_id: str | None
    diameter_mm: float
    exposed: bool
    confidence: float = 0.0
    evidence: list[str] = field(default_factory=list)
