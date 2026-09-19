from __future__ import annotations

from dataclasses import dataclass
from math import atan2, cos, degrees, hypot, isclose, isfinite, pi, radians, sin
from typing import Generic, Iterable, Literal, TypeVar

from shapely.affinity import rotate
from shapely.geometry import GeometryCollection, MultiPolygon, Polygon
from shapely.geometry.base import BaseGeometry
from shapely.geometry.polygon import orient

from .gerber_geometry.arc import ArcSpec, arc_points, segments_for_chord_error
from .gerber_geometry.model import GeoPoint

Polarity = Literal["dark", "clear"]
T = TypeVar("T")


@dataclass(frozen=True)
class ImageOperation(Generic[T]):
    """One ordered Gerber image operation.

    The operation stream is deliberately separate from the reconstructed board
    model. LPC cannot be represented by simply tagging a Track/Pad/Region:
    Gerber polarity is an ordered image-composition operation, so clear objects
    must subtract from the image accumulated before them.
    """

    sequence: int
    polarity: Polarity
    geometry: T


@dataclass(frozen=True)
class PolygonComponent:
    """Canonical polygon shell plus zero or more canonical hole rings."""

    shell: tuple[tuple[float, float], ...]
    holes: tuple[tuple[tuple[float, float], ...], ...] = ()


@dataclass(frozen=True)
class FlashPolygonization:
    """Polygonal flash image plus explicit approximation metadata."""

    geometry: Polygon
    shape: str
    curved_segments: int
    max_chord_error_mm: float
    approximated: bool


@dataclass(frozen=True)
class HoledFlashPolygonization:
    """Polygonal standard aperture flash with one centered round hole."""

    geometry: Polygon
    shape: str
    hole_diameter: float
    outer_curved_segments: int
    hole_curved_segments: int
    max_chord_error_mm: float
    approximated: bool


@dataclass(frozen=True)
class RegularPolygonFlashPolygonization:
    """Exact regular-polygon flash with optional bounded round hole."""

    geometry: Polygon
    vertices: int
    outer_diameter: float
    base_rotation_deg: float
    mirror: str
    object_rotation_deg: float
    hole_diameter: float | None
    hole_curved_segments: int
    max_chord_error_mm: float
    approximated: bool


@dataclass(frozen=True)
class TrackPolygonization:
    """Polygonal circular-aperture linear stroke plus approximation metadata."""

    geometry: Polygon
    length_mm: float
    curved_segments: int
    max_chord_error_mm: float
    approximated: bool


@dataclass(frozen=True)
class ApertureTrackPolygonization:
    """Polygonal linear D01 sweep for a centered C/R/O aperture."""

    geometry: Polygon
    shape: str
    size_x: float
    size_y: float
    rotation_deg: float
    length_mm: float
    curved_segments: int
    max_chord_error_mm: float
    approximated: bool


def polygonize_track(
    start_x: float,
    start_y: float,
    end_x: float,
    end_y: float,
    width: float,
    *,
    max_chord_error_mm: float = 0.005,
    max_arc_segments: int = 4096,
) -> TrackPolygonization:
    """Return a deterministic bounded polygon for a circular-aperture D01 stroke.

    The analytic image is a capsule: an exact rectangular sweep plus two round
    end-caps. Only the curved caps are approximated, using the same symmetric
    inscribed-chord policy as rounded flash polygonization.
    """

    x0 = float(start_x)
    y0 = float(start_y)
    x1 = float(end_x)
    y1 = float(end_y)
    stroke_width = float(width)
    if stroke_width <= 0.0:
        raise ValueError("Gerber track width must be positive")

    length = hypot(x1 - x0, y1 - y0)
    if length <= 1e-15:
        circle = polygonize_flash(
            x0,
            y0,
            stroke_width,
            stroke_width,
            "C",
            max_chord_error_mm=max_chord_error_mm,
            max_arc_segments=max_arc_segments,
        )
        return TrackPolygonization(
            geometry=circle.geometry,
            length_mm=0.0,
            curved_segments=circle.curved_segments,
            max_chord_error_mm=circle.max_chord_error_mm,
            approximated=True,
        )

    cx = (x0 + x1) / 2.0
    cy = (y0 + y1) / 2.0
    capsule = polygonize_flash(
        cx,
        cy,
        length + stroke_width,
        stroke_width,
        "O",
        max_chord_error_mm=max_chord_error_mm,
        max_arc_segments=max_arc_segments,
    )
    angle_deg = degrees(atan2(y1 - y0, x1 - x0))
    geometry = (
        capsule.geometry
        if isclose(angle_deg % 360.0, 0.0, rel_tol=0.0, abs_tol=1e-15)
        else rotate(
            capsule.geometry,
            angle_deg,
            origin=(cx, cy),
            use_radians=False,
        )
    )
    if geometry.is_empty or float(geometry.area) <= 0.0 or not geometry.is_valid:
        raise ValueError("Gerber track polygonization produced invalid geometry")

    return TrackPolygonization(
        geometry=geometry,
        length_mm=length,
        curved_segments=capsule.curved_segments,
        max_chord_error_mm=capsule.max_chord_error_mm,
        approximated=True,
    )


def polygonize_aperture_track(
    start_x: float,
    start_y: float,
    end_x: float,
    end_y: float,
    size_x: float,
    size_y: float,
    shape: str,
    *,
    rotation_deg: float = 0.0,
    max_chord_error_mm: float = 0.005,
    max_arc_segments: int = 4096,
) -> ApertureTrackPolygonization:
    """Return the swept image of a centered C/R/O aperture along a line.

    Rectangular apertures remain polygon-exact at arbitrary finite rotation.
    Circular and obround curved boundaries use the same deterministic
    inscribed-chord policy as flash polygonization.
    The sweep of a convex aperture along a line segment is the convex hull of
    the aperture translated to the two segment endpoints.
    """

    x0 = float(start_x)
    y0 = float(start_y)
    x1 = float(end_x)
    y1 = float(end_y)
    sx = float(size_x)
    sy = float(size_y)
    kind = str(shape).upper()
    rotation = float(rotation_deg)
    if not isfinite(rotation):
        raise ValueError("Gerber aperture-track rotation must be finite")
    rotation %= 360.0

    if sx <= 0.0 or sy <= 0.0:
        raise ValueError("Gerber aperture-track dimensions must be positive")
    if kind not in {"C", "R", "O"}:
        raise ValueError(
            f"unsupported Gerber aperture shape for track polygonization: {kind!r}"
        )

    length = hypot(x1 - x0, y1 - y0)
    if kind == "C":
        if not isclose(sx, sy, rel_tol=1e-12, abs_tol=1e-12):
            raise ValueError("circular Gerber aperture track must have equal X/Y dimensions")
        track = polygonize_track(
            x0,
            y0,
            x1,
            y1,
            sx,
            max_chord_error_mm=max_chord_error_mm,
            max_arc_segments=max_arc_segments,
        )
        return ApertureTrackPolygonization(
            geometry=track.geometry,
            shape=kind,
            size_x=sx,
            size_y=sy,
            rotation_deg=rotation,
            length_mm=track.length_mm,
            curved_segments=track.curved_segments,
            max_chord_error_mm=track.max_chord_error_mm,
            approximated=track.approximated,
        )

    start_flash = polygonize_flash(
        x0,
        y0,
        sx,
        sy,
        kind,
        max_chord_error_mm=max_chord_error_mm,
        max_arc_segments=max_arc_segments,
    )
    start_geometry = start_flash.geometry
    if not isclose(rotation, 0.0, rel_tol=0.0, abs_tol=1e-15):
        start_geometry = rotate(
            start_geometry,
            rotation,
            origin=(x0, y0),
            use_radians=False,
        )

    if length <= 1e-15:
        geometry = start_geometry
    else:
        end_flash = polygonize_flash(
            x1,
            y1,
            sx,
            sy,
            kind,
            max_chord_error_mm=max_chord_error_mm,
            max_arc_segments=max_arc_segments,
        )
        end_geometry = end_flash.geometry
        if not isclose(rotation, 0.0, rel_tol=0.0, abs_tol=1e-15):
            end_geometry = rotate(
                end_geometry,
                rotation,
                origin=(x1, y1),
                use_radians=False,
            )
        geometry = start_geometry.union(end_geometry).convex_hull

    if not isinstance(geometry, Polygon):
        raise ValueError("Gerber aperture-track sweep produced non-polygonal geometry")
    if geometry.is_empty or float(geometry.area) <= 0.0 or not geometry.is_valid:
        raise ValueError("Gerber aperture-track polygonization produced invalid geometry")

    return ApertureTrackPolygonization(
        geometry=geometry,
        shape=kind,
        size_x=sx,
        size_y=sy,
        rotation_deg=rotation,
        length_mm=length,
        curved_segments=start_flash.curved_segments,
        max_chord_error_mm=start_flash.max_chord_error_mm,
        approximated=start_flash.approximated,
    )


@dataclass(frozen=True)
class ImageOperationContribution:
    """Effective ordered contribution from one image operation.

    Dark contribution geometry is surviving material that operation actually
    added. Clear contribution geometry is boundary that operation actually
    created at the time it erased material. Consumers may intersect these
    contributions with final components to derive component-local provenance.
    """

    sequence: int
    polarity: Polarity
    geometry: BaseGeometry


@dataclass(frozen=True)
class PolygonCompositionTrace:
    """Final polygonal image plus effective per-operation contributions."""

    image: Polygon | MultiPolygon | GeometryCollection
    contributions: tuple[ImageOperationContribution, ...]


def polygonize_flash(
    center_x: float,
    center_y: float,
    size_x: float,
    size_y: float,
    shape: str,
    *,
    max_chord_error_mm: float = 0.005,
    max_arc_segments: int = 4096,
) -> FlashPolygonization:
    """Return deterministic polygon geometry for solid C/R/O Gerber flashes.

    Rectangles are exact. Circles and obround end-caps are represented by
    inscribed chords chosen with the same sagitta bound used for Gerber arc
    tessellation. The approximation is therefore conservative for both dark
    and clear image operations and has an explicit maximum boundary error.
    """

    cx = float(center_x)
    cy = float(center_y)
    sx = float(size_x)
    sy = float(size_y)
    kind = str(shape).upper()

    if sx <= 0.0 or sy <= 0.0:
        raise ValueError("Gerber flash dimensions must be positive")
    if max_chord_error_mm <= 0.0:
        raise ValueError("max_chord_error_mm must be positive")
    if max_arc_segments < 1:
        raise ValueError("max_arc_segments must be positive")

    if kind == "R":
        geometry = Polygon(
            (
                (cx - sx / 2.0, cy - sy / 2.0),
                (cx + sx / 2.0, cy - sy / 2.0),
                (cx + sx / 2.0, cy + sy / 2.0),
                (cx - sx / 2.0, cy + sy / 2.0),
            )
        )
        return FlashPolygonization(
            geometry=geometry,
            shape=kind,
            curved_segments=0,
            max_chord_error_mm=0.0,
            approximated=False,
        )

    if kind == "C":
        if not isclose(sx, sy, rel_tol=1e-12, abs_tol=1e-12):
            raise ValueError("circular Gerber flash must have equal X/Y dimensions")
        points = _circle_points(
            cx,
            cy,
            sx / 2.0,
            max_chord_error_mm=max_chord_error_mm,
            max_arc_segments=max_arc_segments,
        )
        geometry = Polygon(points)
        _validate_flash_polygon(geometry)
        return FlashPolygonization(
            geometry=geometry,
            shape=kind,
            curved_segments=len(points) - 1,
            max_chord_error_mm=max_chord_error_mm,
            approximated=True,
        )

    if kind == "O":
        if isclose(sx, sy, rel_tol=1e-12, abs_tol=1e-12):
            points = _circle_points(
                cx,
                cy,
                sx / 2.0,
                max_chord_error_mm=max_chord_error_mm,
                max_arc_segments=max_arc_segments,
            )
            geometry = Polygon(points)
            _validate_flash_polygon(geometry)
            return FlashPolygonization(
                geometry=geometry,
                shape=kind,
                curved_segments=len(points) - 1,
                max_chord_error_mm=max_chord_error_mm,
                approximated=True,
            )

        if sx > sy:
            radius = sy / 2.0
            half_straight = (sx - sy) / 2.0
            left = _arc_polygon_points(
                start=GeoPoint(cx - half_straight, cy + radius),
                end=GeoPoint(cx - half_straight, cy - radius),
                center=GeoPoint(cx - half_straight, cy),
                max_chord_error_mm=max_chord_error_mm,
                max_arc_segments=max_arc_segments,
            )
            right = _arc_polygon_points(
                start=GeoPoint(cx + half_straight, cy - radius),
                end=GeoPoint(cx + half_straight, cy + radius),
                center=GeoPoint(cx + half_straight, cy),
                max_chord_error_mm=max_chord_error_mm,
                max_arc_segments=max_arc_segments,
            )
            coords = [*left, *right]
        else:
            radius = sx / 2.0
            half_straight = (sy - sx) / 2.0
            bottom = _arc_polygon_points(
                start=GeoPoint(cx - radius, cy - half_straight),
                end=GeoPoint(cx + radius, cy - half_straight),
                center=GeoPoint(cx, cy - half_straight),
                max_chord_error_mm=max_chord_error_mm,
                max_arc_segments=max_arc_segments,
            )
            top = _arc_polygon_points(
                start=GeoPoint(cx + radius, cy + half_straight),
                end=GeoPoint(cx - radius, cy + half_straight),
                center=GeoPoint(cx, cy + half_straight),
                max_chord_error_mm=max_chord_error_mm,
                max_arc_segments=max_arc_segments,
            )
            coords = [*bottom, *top]

        geometry = Polygon(coords)
        _validate_flash_polygon(geometry)
        return FlashPolygonization(
            geometry=geometry,
            shape=kind,
            curved_segments=(len(coords) - 2),
            max_chord_error_mm=max_chord_error_mm,
            approximated=True,
        )

    raise ValueError(f"unsupported Gerber flash shape for polygonization: {kind!r}")


def polygonize_rotated_flash(
    center_x: float,
    center_y: float,
    size_x: float,
    size_y: float,
    shape: str,
    *,
    rotation_deg: float = 0.0,
    max_chord_error_mm: float = 0.005,
    max_arc_segments: int = 4096,
) -> FlashPolygonization:
    """Return a solid C/R/O flash polygon at an arbitrary finite rotation."""

    rotation = float(rotation_deg)
    if not isfinite(rotation):
        raise ValueError("Gerber flash rotation must be finite")
    rotation %= 360.0

    base = polygonize_flash(
        center_x,
        center_y,
        size_x,
        size_y,
        shape,
        max_chord_error_mm=max_chord_error_mm,
        max_arc_segments=max_arc_segments,
    )
    geometry = base.geometry
    if not isclose(rotation, 0.0, rel_tol=0.0, abs_tol=1e-15):
        geometry = rotate(
            geometry,
            rotation,
            origin=(float(center_x), float(center_y)),
            use_radians=False,
        )
    if not isinstance(geometry, Polygon):
        raise ValueError("Gerber rotated flash produced non-polygonal geometry")
    _validate_flash_polygon(geometry)
    return FlashPolygonization(
        geometry=geometry,
        shape=base.shape,
        curved_segments=base.curved_segments,
        max_chord_error_mm=base.max_chord_error_mm,
        approximated=base.approximated,
    )


def polygonize_holed_flash(
    center_x: float,
    center_y: float,
    size_x: float,
    size_y: float,
    shape: str,
    hole_diameter: float,
    *,
    rotation_deg: float = 0.0,
    max_chord_error_mm: float = 0.005,
    max_arc_segments: int = 4096,
) -> HoledFlashPolygonization:
    """Return the solid part of a standard C/R/O flash with a round hole.

    Gerber aperture holes are transparent: the hole is excluded from this
    operation geometry rather than emitted as a separate clear operation.
    """

    sx = float(size_x)
    sy = float(size_y)
    hole = float(hole_diameter)
    kind = str(shape).upper()
    if hole <= 0.0:
        raise ValueError("Gerber aperture hole diameter must be positive")
    if hole >= min(sx, sy):
        raise ValueError("Gerber aperture hole must strictly fit within aperture")

    outer = polygonize_rotated_flash(
        center_x,
        center_y,
        sx,
        sy,
        kind,
        rotation_deg=rotation_deg,
        max_chord_error_mm=max_chord_error_mm,
        max_arc_segments=max_arc_segments,
    )
    hole_poly = polygonize_flash(
        center_x,
        center_y,
        hole,
        hole,
        "C",
        max_chord_error_mm=max_chord_error_mm,
        max_arc_segments=max_arc_segments,
    )
    geometry = outer.geometry.difference(hole_poly.geometry)
    if not isinstance(geometry, Polygon):
        raise ValueError("Gerber holed flash produced non-polygonal geometry")
    if (
        geometry.is_empty
        or float(geometry.area) <= 0.0
        or not geometry.is_valid
        or len(geometry.interiors) != 1
    ):
        raise ValueError("Gerber holed flash did not preserve one centered hole")

    return HoledFlashPolygonization(
        geometry=geometry,
        shape=kind,
        hole_diameter=hole,
        outer_curved_segments=outer.curved_segments,
        hole_curved_segments=hole_poly.curved_segments,
        max_chord_error_mm=max(
            outer.max_chord_error_mm,
            hole_poly.max_chord_error_mm,
        ),
        approximated=outer.approximated or hole_poly.approximated,
    )


def polygonize_regular_polygon_flash(
    center_x: float,
    center_y: float,
    outer_diameter: float,
    vertices: int,
    *,
    base_rotation_deg: float = 0.0,
    mirror: str = "N",
    object_rotation_deg: float = 0.0,
    hole_diameter: float | None = None,
    max_chord_error_mm: float = 0.005,
    max_arc_segments: int = 4096,
) -> RegularPolygonFlashPolygonization:
    """Return exact regular-polygon D03 geometry with optional round hole.

    The polygon template rotation belongs to the original aperture. LM mirroring
    is applied to that original shape before the modal LR/object rotation.
    """

    cx = float(center_x)
    cy = float(center_y)
    diameter = float(outer_diameter)
    if diameter <= 0.0:
        raise ValueError("Gerber polygon outer diameter must be positive")
    if isinstance(vertices, bool) or int(vertices) != vertices:
        raise ValueError("Gerber polygon vertex count must be an integer")
    vertex_count = int(vertices)
    if not 3 <= vertex_count <= 12:
        raise ValueError("Gerber polygon vertex count must be in 3..12")

    base_rotation = float(base_rotation_deg)
    object_rotation = float(object_rotation_deg)
    if not isfinite(base_rotation) or not isfinite(object_rotation):
        raise ValueError("Gerber polygon rotation must be finite")
    mirror_mode = str(mirror).upper()
    if mirror_mode not in {"N", "X", "Y", "XY"}:
        raise ValueError(f"invalid Gerber aperture mirror mode: {mirror_mode!r}")

    radius = diameter / 2.0
    points: list[tuple[float, float]] = []
    for index in range(vertex_count):
        angle = radians(base_rotation + index * 360.0 / vertex_count)
        dx = radius * cos(angle)
        dy = radius * sin(angle)
        if "X" in mirror_mode:
            dx = -dx
        if "Y" in mirror_mode:
            dy = -dy
        rotation = radians(object_rotation)
        rx = dx * cos(rotation) - dy * sin(rotation)
        ry = dx * sin(rotation) + dy * cos(rotation)
        points.append((cx + rx, cy + ry))

    outer = Polygon(points)
    _validate_flash_polygon(outer)

    hole = None if hole_diameter is None else float(hole_diameter)
    hole_segments = 0
    approximated = False
    geometry = outer
    if hole is not None:
        if hole <= 0.0:
            raise ValueError("Gerber polygon hole diameter must be positive")
        max_hole = diameter * cos(pi / vertex_count)
        if hole >= max_hole:
            raise ValueError(
                "Gerber polygon round hole must strictly fit within polygon"
            )
        hole_poly = polygonize_flash(
            cx,
            cy,
            hole,
            hole,
            "C",
            max_chord_error_mm=max_chord_error_mm,
            max_arc_segments=max_arc_segments,
        )
        geometry = outer.difference(hole_poly.geometry)
        hole_segments = hole_poly.curved_segments
        approximated = hole_poly.approximated
        if not isinstance(geometry, Polygon) or len(geometry.interiors) != 1:
            raise ValueError(
                "Gerber polygon holed flash did not preserve one centered hole"
            )
        _validate_flash_polygon(geometry)

    return RegularPolygonFlashPolygonization(
        geometry=geometry,
        vertices=vertex_count,
        outer_diameter=diameter,
        base_rotation_deg=base_rotation % 360.0,
        mirror=mirror_mode,
        object_rotation_deg=object_rotation % 360.0,
        hole_diameter=hole,
        hole_curved_segments=hole_segments,
        max_chord_error_mm=(max_chord_error_mm if hole is not None else 0.0),
        approximated=approximated,
    )


def polygonize_regular_polygon_track(
    start_x: float,
    start_y: float,
    end_x: float,
    end_y: float,
    outer_diameter: float,
    vertices: int,
    *,
    base_rotation_deg: float = 0.0,
    mirror: str = "N",
    object_rotation_deg: float = 0.0,
) -> ApertureTrackPolygonization:
    """Return the exact linear sweep of a solid regular-polygon aperture."""

    x0 = float(start_x)
    y0 = float(start_y)
    x1 = float(end_x)
    y1 = float(end_y)
    diameter = float(outer_diameter)

    start_flash = polygonize_regular_polygon_flash(
        x0,
        y0,
        diameter,
        vertices,
        base_rotation_deg=base_rotation_deg,
        mirror=mirror,
        object_rotation_deg=object_rotation_deg,
    )
    length = hypot(x1 - x0, y1 - y0)
    if length <= 1e-15:
        geometry = start_flash.geometry
    else:
        end_flash = polygonize_regular_polygon_flash(
            x1,
            y1,
            diameter,
            vertices,
            base_rotation_deg=base_rotation_deg,
            mirror=mirror,
            object_rotation_deg=object_rotation_deg,
        )
        geometry = start_flash.geometry.union(end_flash.geometry).convex_hull

    if not isinstance(geometry, Polygon):
        raise ValueError("Gerber polygon track sweep produced non-polygonal geometry")
    if geometry.is_empty or float(geometry.area) <= 0.0 or not geometry.is_valid:
        raise ValueError("Gerber polygon track sweep produced invalid geometry")

    return ApertureTrackPolygonization(
        geometry=geometry,
        shape="P",
        size_x=diameter,
        size_y=diameter,
        rotation_deg=float(object_rotation_deg) % 360.0,
        length_mm=length,
        curved_segments=0,
        max_chord_error_mm=0.0,
        approximated=False,
    )


def _circle_points(
    cx: float,
    cy: float,
    radius: float,
    *,
    max_chord_error_mm: float,
    max_arc_segments: int,
) -> list[tuple[float, float]]:
    start = GeoPoint(cx + radius, cy)
    spec = ArcSpec(start=start, end=start, center=GeoPoint(cx, cy), clockwise=False)
    segments = segments_for_chord_error(
        spec,
        max_chord_error_mm,
        max_segments=max_arc_segments,
    )
    segments += (-segments) % 4
    if segments > max_arc_segments:
        raise ValueError(
            "circle flash tessellation symmetry would exceed max_arc_segments"
        )
    points = arc_points(spec, segments=segments)
    return [(point.x, point.y) for point in points]


def _arc_polygon_points(
    *,
    start: GeoPoint,
    end: GeoPoint,
    center: GeoPoint,
    max_chord_error_mm: float,
    max_arc_segments: int,
) -> list[tuple[float, float]]:
    spec = ArcSpec(start=start, end=end, center=center, clockwise=False)
    segments = segments_for_chord_error(
        spec,
        max_chord_error_mm,
        max_segments=max_arc_segments,
    )
    segments += segments % 2
    if segments > max_arc_segments:
        raise ValueError(
            "obround cap tessellation symmetry would exceed max_arc_segments"
        )
    points = arc_points(spec, segments=segments)
    return [(point.x, point.y) for point in points]


def _validate_flash_polygon(geometry: Polygon) -> None:
    if geometry.is_empty or float(geometry.area) <= 0.0 or not geometry.is_valid:
        raise ValueError("Gerber flash polygonization produced invalid geometry")


class ImageCompositionStream(Generic[T]):
    """Deterministic ordered dark/clear operation stream.

    Consumers must compose operations in sequence order; grouping by polarity
    changes Gerber semantics whenever dark geometry follows a clear operation.
    """

    def __init__(self) -> None:
        self._operations: list[ImageOperation[T]] = []
        self._next_sequence = 0

    def append(self, polarity: Polarity, geometry: T) -> ImageOperation[T]:
        if polarity not in {"dark", "clear"}:
            raise ValueError(f"invalid Gerber image polarity: {polarity!r}")
        op = ImageOperation(self._next_sequence, polarity, geometry)
        self._operations.append(op)
        self._next_sequence += 1
        return op

    @property
    def operations(self) -> tuple[ImageOperation[T], ...]:
        return tuple(self._operations)

    def clear(self) -> None:
        self._operations.clear()
        self._next_sequence = 0


def trace_polygon_operation_contributions(
    operations: Iterable[ImageOperation[BaseGeometry]],
) -> PolygonCompositionTrace:
    """Trace effective ordered contributions while composing a Gerber image.

    A dark operation contributes only material that was not already dark when
    the operation occurred, and that material is reduced by every later clear
    operation. A clear operation contributes only boundary newly created by an
    actual subtraction. This prevents redundant/erased operations from leaking
    into final component provenance while preserving source-order semantics.
    """

    items = tuple(operations)
    image: BaseGeometry = GeometryCollection()
    dark_material: dict[int, BaseGeometry] = {}
    clear_boundaries: dict[int, BaseGeometry] = {}
    expected_sequence = 0

    for operation in items:
        if operation.sequence != expected_sequence:
            raise ValueError(
                "Gerber image operations must be contiguous and ordered by sequence"
            )
        expected_sequence += 1

        geometry = operation.geometry
        if not isinstance(geometry, (Polygon, MultiPolygon)):
            raise TypeError(
                "Gerber polygon contribution tracing requires Polygon or "
                "MultiPolygon geometry"
            )
        if not geometry.is_valid:
            raise ValueError(
                "Gerber polygon contribution tracing received invalid geometry"
            )

        if geometry.is_empty:
            if operation.polarity == "dark":
                dark_material[operation.sequence] = GeometryCollection()
            elif operation.polarity == "clear":
                clear_boundaries[operation.sequence] = GeometryCollection()
            else:
                raise ValueError(
                    f"invalid Gerber image polarity: {operation.polarity!r}"
                )
            continue

        before = image
        if operation.polarity == "dark":
            added = geometry.difference(before)
            dark_material[operation.sequence] = added
            image = before.union(geometry)
        elif operation.polarity == "clear":
            after = before.difference(geometry)
            after_boundary = _safe_boundary(after)
            before_boundary = _safe_boundary(before)
            clear_boundaries[operation.sequence] = after_boundary.difference(
                before_boundary
            )
            for sequence, surviving in tuple(dark_material.items()):
                if surviving.is_empty:
                    continue
                dark_material[sequence] = surviving.difference(geometry)
            image = after
        else:
            raise ValueError(f"invalid Gerber image polarity: {operation.polarity!r}")

        if not image.is_valid:
            raise ValueError(
                "Gerber polygon contribution tracing produced invalid geometry"
            )

    final_image = _normalize_polygonal_image(
        image,
        error_prefix="Gerber polygon contribution tracing",
    )
    contributions = tuple(
        ImageOperationContribution(
            operation.sequence,
            operation.polarity,
            (
                dark_material.get(operation.sequence, GeometryCollection())
                if operation.polarity == "dark"
                else clear_boundaries.get(operation.sequence, GeometryCollection())
            ),
        )
        for operation in items
    )
    return PolygonCompositionTrace(final_image, contributions)


def compose_polygon_operations(
    operations: Iterable[ImageOperation[BaseGeometry]],
) -> Polygon | MultiPolygon | GeometryCollection:
    """Compose ordered polygonal Gerber image operations.

    Dark operations union material into the current image. Clear operations
    subtract material from the image accumulated *so far*. Inputs must be valid
    Polygon/MultiPolygon geometry. Empty inputs are accepted as no-ops. The
    result is empty, Polygon, or MultiPolygon; any non-polygonal result fails
    closed rather than being silently discarded.
    """

    image: BaseGeometry = GeometryCollection()
    expected_sequence = 0

    for operation in operations:
        if operation.sequence != expected_sequence:
            raise ValueError(
                "Gerber image operations must be contiguous and ordered by sequence"
            )
        expected_sequence += 1

        geometry = operation.geometry
        if not isinstance(geometry, (Polygon, MultiPolygon)):
            raise TypeError(
                "Gerber polygon composition requires Polygon or MultiPolygon geometry"
            )
        if not geometry.is_valid:
            raise ValueError("Gerber polygon composition received invalid geometry")
        if geometry.is_empty:
            continue

        if operation.polarity == "dark":
            image = image.union(geometry)
        elif operation.polarity == "clear":
            image = image.difference(geometry)
        else:
            raise ValueError(f"invalid Gerber image polarity: {operation.polarity!r}")

        if not image.is_valid:
            raise ValueError("Gerber polygon composition produced invalid geometry")

    return _normalize_polygonal_image(
        image,
        error_prefix="Gerber polygon composition",
    )


def _safe_boundary(geometry: BaseGeometry) -> BaseGeometry:
    """Return an empty geometry instead of Shapely's None empty boundary."""
    if geometry.is_empty:
        return GeometryCollection()
    boundary = geometry.boundary
    return boundary if boundary is not None else GeometryCollection()


def _normalize_polygonal_image(
    image: BaseGeometry,
    *,
    error_prefix: str,
) -> Polygon | MultiPolygon | GeometryCollection:
    if image.is_empty:
        return GeometryCollection()
    if not isinstance(image, (Polygon, MultiPolygon)):
        raise ValueError(f"{error_prefix} produced non-polygonal residual geometry")
    return image


def canonical_polygon_components(
    geometry: Polygon | MultiPolygon | GeometryCollection,
) -> tuple[PolygonComponent, ...]:
    """Return deterministic shell/hole rings for a composed polygonal image.

    Shells are normalized counter-clockwise, holes clockwise, every ring starts
    at its lexicographically smallest vertex, and components/holes are sorted.
    The closing vertex is retained so callers can materialize closed rings
    without inventing topology.
    """

    if geometry.is_empty:
        return ()
    if not isinstance(geometry, (Polygon, MultiPolygon)):
        raise TypeError("canonical polygon components require polygonal geometry")
    if not geometry.is_valid:
        raise ValueError("cannot canonicalize invalid polygonal geometry")

    polygons = [geometry] if isinstance(geometry, Polygon) else list(geometry.geoms)
    components: list[PolygonComponent] = []

    for polygon in polygons:
        normalized = orient(polygon, sign=1.0)
        shell = _canonical_ring(normalized.exterior.coords)
        holes = tuple(
            sorted(_canonical_ring(ring.coords) for ring in normalized.interiors)
        )
        components.append(PolygonComponent(shell=shell, holes=holes))

    return tuple(
        sorted(
            components,
            key=lambda component: (component.shell, component.holes),
        )
    )


def _canonical_ring(coords) -> tuple[tuple[float, float], ...]:
    points = [(float(x), float(y)) for x, y in coords]
    if len(points) < 4 or points[0] != points[-1]:
        raise ValueError("polygon ring must be explicitly closed")

    open_ring = points[:-1]
    start = min(range(len(open_ring)), key=lambda index: open_ring[index])
    rotated = open_ring[start:] + open_ring[:start]
    rotated.append(rotated[0])
    return tuple(rotated)
