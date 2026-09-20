from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class DrcIssue:
    severity: str
    code: str
    message: str
    object_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class DrcConfig:
    min_track_width_mm: float = 0.15
    min_drill_mm: float = 0.2
    min_annular_ring_mm: float = 0.1
    min_clearance_mm: float = 0.15
    edge_clearance_mm: float = 0.2
    min_drill_copper_clearance_mm: float = 0.15
    min_mechanical_copper_clearance_mm: float = 0.15

    def __post_init__(self):
        for name in (
            "min_track_width_mm",
            "min_drill_mm",
            "min_annular_ring_mm",
            "min_clearance_mm",
            "edge_clearance_mm",
            "min_drill_copper_clearance_mm",
            "min_mechanical_copper_clearance_mm",
        ):
            value = getattr(self, name)
            if isinstance(value, (str, bytes, bool)):
                raise ValueError(f"{name} must be a finite non-negative number")
            try:
                numeric = float(value)
            except (TypeError, ValueError):
                raise ValueError(f"{name} must be a finite non-negative number") from None
            if not isfinite(numeric) or numeric < 0.0:
                raise ValueError(f"{name} must be a finite non-negative number")
            object.__setattr__(self, name, numeric)
