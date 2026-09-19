from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Iterable, Literal, TypeVar

from shapely.geometry import GeometryCollection, MultiPolygon, Polygon
from shapely.geometry.base import BaseGeometry
from shapely.geometry.polygon import orient

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

    if image.is_empty:
        return GeometryCollection()
    if not isinstance(image, (Polygon, MultiPolygon)):
        raise ValueError(
            "Gerber polygon composition produced non-polygonal residual geometry"
        )
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
