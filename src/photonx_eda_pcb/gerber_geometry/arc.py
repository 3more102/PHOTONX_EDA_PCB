from __future__ import annotations

from dataclasses import dataclass
from math import acos, atan2, ceil, cos, hypot, isclose, pi, sin

from .model import GeoPoint


@dataclass(frozen=True)
class ArcSpec:
    start: GeoPoint
    end: GeoPoint
    center: GeoPoint
    clockwise: bool = False


def arc_radii(spec: ArcSpec) -> tuple[float, float]:
    return (
        hypot(spec.start.x - spec.center.x, spec.start.y - spec.center.y),
        hypot(spec.end.x - spec.center.x, spec.end.y - spec.center.y),
    )


def validate_arc(
    spec: ArcSpec,
    *,
    rel_tol: float = 1e-6,
    abs_tol: float = 1e-6,
) -> float:
    """Validate center-offset arc geometry and return its radius."""
    start_radius, end_radius = arc_radii(spec)
    if start_radius <= abs_tol:
        raise ValueError("arc radius must be positive")
    if not isclose(start_radius, end_radius, rel_tol=rel_tol, abs_tol=abs_tol):
        raise ValueError(
            "arc start/end radii differ: "
            f"{start_radius:.12g} vs {end_radius:.12g}"
        )
    return start_radius


def sweep_radians(spec: ArcSpec) -> float:
    validate_arc(spec)
    a = atan2(spec.start.y - spec.center.y, spec.start.x - spec.center.x)
    b = atan2(spec.end.y - spec.center.y, spec.end.x - spec.center.x)
    delta = b - a
    if spec.clockwise:
        if delta >= 0:
            delta -= 2 * pi
    elif delta <= 0:
        delta += 2 * pi
    return delta


def segments_for_chord_error(
    spec: ArcSpec,
    max_chord_error_mm: float = 0.005,
    *,
    max_segments: int = 4096,
) -> int:
    """Choose a deterministic tessellation count bounded by chord sagitta."""
    if max_chord_error_mm <= 0:
        raise ValueError("max_chord_error_mm must be positive")
    if max_segments < 1:
        raise ValueError("max_segments must be positive")

    radius = validate_arc(spec)
    sweep = abs(sweep_radians(spec))
    topology_limit = pi / 2

    ratio = min(max_chord_error_mm / radius, 2.0)
    theta = 2 * acos(max(-1.0, min(1.0, 1.0 - ratio)))
    theta = min(topology_limit, theta) if theta > 0 else topology_limit
    count = max(1, ceil(sweep / theta))

    if count > max_segments:
        raise ValueError(
            f"arc tessellation requires {count} segments; limit is {max_segments}"
        )
    return count


def arc_points(
    spec: ArcSpec,
    segments: int | None = 32,
    *,
    max_chord_error_mm: float = 0.005,
    max_segments: int = 4096,
) -> list[GeoPoint]:
    """Return deterministic arc points.

    Passing segments=None enables adaptive tessellation using the requested
    maximum chord error. Explicit segments remains supported for compatibility.
    """
    radius = validate_arc(spec)
    if segments is None:
        segments = segments_for_chord_error(
            spec,
            max_chord_error_mm,
            max_segments=max_segments,
        )
    if segments < 1:
        raise ValueError("segments must be positive")

    start_angle = atan2(
        spec.start.y - spec.center.y,
        spec.start.x - spec.center.x,
    )
    sweep = sweep_radians(spec)
    points = [
        GeoPoint(
            spec.center.x + radius * cos(start_angle + sweep * i / segments),
            spec.center.y + radius * sin(start_angle + sweep * i / segments),
        )
        for i in range(segments + 1)
    ]
    points[0] = spec.start
    points[-1] = spec.end
    return points
