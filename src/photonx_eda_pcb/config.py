from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class ReconstructionConfig:
    strict_parsing: bool = True
    connectivity_tolerance_mm: float = 0.03
    drill_attach_tolerance_mm: float = 0.15
    component_pair_distance_mm: float = 4.0
    min_component_confidence: float = 0.45
