from __future__ import annotations
from dataclasses import dataclass, field, asdict

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
    layer: str = "F.Cu"
    net: str | None = None

@dataclass
class Pad:
    id: str
    center: Point
    diameter: float
    layer: str = "F.Cu"
    drill: float | None = None
    net: str | None = None

@dataclass
class Hole:
    id: str
    center: Point
    diameter: float
    plated: bool = True

@dataclass
class Outline:
    segments: list[Track] = field(default_factory=list)

@dataclass
class ComponentHypothesis:
    id: str
    pad_ids: list[str]
    kind: str
    confidence: float
    evidence: list[str]

@dataclass
class BoardModel:
    tracks: list[Track] = field(default_factory=list)
    pads: list[Pad] = field(default_factory=list)
    holes: list[Hole] = field(default_factory=list)
    outline: Outline = field(default_factory=Outline)
    components: list[ComponentHypothesis] = field(default_factory=list)
    nets: dict[str, list[str]] = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)
