from __future__ import annotations
from dataclasses import dataclass, field, asdict
from .provenance import Provenance
from .mechanical_features.model import SlotFeature

@dataclass(frozen=True)
class Point:
    x: float
    y: float

@dataclass
class Track:
    id: str
    start: Point
    end: Point
    width: float
    layer: str
    net_id: str | None = None
    provenance: Provenance = field(default_factory=Provenance)

@dataclass
class PadCandidate:
    id: str
    center: Point
    size_x: float
    size_y: float
    shape: str
    layer: str
    drill: float | None = None
    net_id: str | None = None
    provenance: Provenance = field(default_factory=Provenance)

@dataclass
class DrillHit:
    id: str
    center: Point
    diameter: float
    plating: str = "unknown"
    tool: str | None = None
    provenance: Provenance = field(default_factory=Provenance)

@dataclass
class OutlineSegment:
    id: str
    start: Point
    end: Point
    provenance: Provenance = field(default_factory=Provenance)

@dataclass
class NetGroup:
    id: str
    members: list[str]
    confidence: float
    label: str | None = None
    provenance: Provenance = field(default_factory=Provenance)

@dataclass
class ComponentHypothesis:
    id: str
    pad_ids: list[str]
    kind: str
    confidence: float
    evidence: list[str]
    reference: str | None = None

@dataclass
class ParseDiagnostic:
    severity: str
    code: str
    message: str
    path: str
    line: int | None = None

@dataclass
class BoardModel:
    tracks: list[Track] = field(default_factory=list)
    pads: list[PadCandidate] = field(default_factory=list)
    drills: list[DrillHit] = field(default_factory=list)
    outline: list[OutlineSegment] = field(default_factory=list)
    nets: list[NetGroup] = field(default_factory=list)
    components: list[ComponentHypothesis] = field(default_factory=list)
    diagnostics: list[ParseDiagnostic] = field(default_factory=list)
    metadata: dict[str, object] = field(default_factory=dict)
    slots: list[SlotFeature] = field(default_factory=list)

    def object_index(self) -> dict[str, object]:
        items = [*self.tracks, *self.pads, *self.drills, *self.outline, *self.slots]
        return {obj.id: obj for obj in items}

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
