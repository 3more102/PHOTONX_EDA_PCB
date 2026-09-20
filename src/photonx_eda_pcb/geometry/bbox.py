from dataclasses import dataclass

from ..models import BoardModel, Point


@dataclass(frozen=True)
class Bounds:
    min_x: float
    min_y: float
    max_x: float
    max_y: float

    @property
    def width(self):
        return self.max_x - self.min_x

    @property
    def height(self):
        return self.max_y - self.min_y


def bounds_from_points(points: list[Point]) -> Bounds | None:
    if not points:
        return None
    xs = [p.x for p in points]
    ys = [p.y for p in points]
    return Bounds(min(xs), min(ys), max(xs), max(ys))


def _append_extent(
    points: list[Point],
    x: float,
    y: float,
    half_width: float = 0.0,
    half_height: float | None = None,
) -> None:
    half_height = half_width if half_height is None else half_height
    half_width = abs(half_width)
    half_height = abs(half_height)
    points.extend(
        [
            Point(x - half_width, y - half_height),
            Point(x + half_width, y + half_height),
        ]
    )


def board_bounds(board: BoardModel) -> Bounds | None:
    """Return bounds covering all first-class physical board geometry."""

    points: list[Point] = []

    for track in board.tracks:
        radius = track.width / 2.0
        _append_extent(points, track.start.x, track.start.y, radius)
        _append_extent(points, track.end.x, track.end.y, radius)

    for pad in board.pads:
        _append_extent(
            points,
            pad.center.x,
            pad.center.y,
            pad.size_x / 2.0,
            pad.size_y / 2.0,
        )

    for drill in board.drills:
        _append_extent(
            points,
            drill.center.x,
            drill.center.y,
            drill.diameter / 2.0,
        )

    for segment in board.outline:
        points.extend([segment.start, segment.end])

    for slot in board.slots:
        radius = slot.width_mm / 2.0
        _append_extent(points, slot.start[0], slot.start[1], radius)
        _append_extent(points, slot.end[0], slot.end[1], radius)

    for route in board.routes:
        radius = route.width_mm / 2.0
        for x, y in route.points:
            _append_extent(points, x, y, radius)

    for region in board.regions:
        points.extend(region.points)
        for hole in region.holes:
            points.extend(hole)

    return bounds_from_points(points)
