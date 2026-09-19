from __future__ import annotations

from collections.abc import Iterable

from ..models import BoardModel


Bounds = tuple[float, float, float, float]


def _include_points(
    bounds: Bounds | None,
    points: Iterable[tuple[float, float]],
    *,
    radius: float = 0.0,
) -> Bounds | None:
    current = bounds
    for x, y in points:
        xmin = x - radius
        ymin = y - radius
        xmax = x + radius
        ymax = y + radius
        if current is None:
            current = (xmin, ymin, xmax, ymax)
        else:
            current = (
                min(current[0], xmin),
                min(current[1], ymin),
                max(current[2], xmax),
                max(current[3], ymax),
            )
    return current


def board_bounds(board: BoardModel) -> Bounds | None:
    """Return physical extents for every renderable board-evidence object."""

    bounds: Bounds | None = None

    for track in board.tracks:
        bounds = _include_points(
            bounds,
            ((track.start.x, track.start.y), (track.end.x, track.end.y)),
            radius=max(0.0, track.width) / 2,
        )

    for pad in board.pads:
        half_x = max(0.0, pad.size_x) / 2
        half_y = max(0.0, pad.size_y) / 2
        bounds = _include_points(
            bounds,
            (
                (pad.center.x - half_x, pad.center.y - half_y),
                (pad.center.x + half_x, pad.center.y + half_y),
            ),
        )

    for drill in board.drills:
        bounds = _include_points(
            bounds,
            ((drill.center.x, drill.center.y),),
            radius=max(0.0, drill.diameter) / 2,
        )

    for segment in board.outline:
        bounds = _include_points(
            bounds,
            ((segment.start.x, segment.start.y), (segment.end.x, segment.end.y)),
        )

    for slot in board.slots:
        bounds = _include_points(
            bounds,
            (slot.start, slot.end),
            radius=max(0.0, slot.width_mm) / 2,
        )

    for route in board.routes:
        bounds = _include_points(
            bounds,
            route.points,
            radius=max(0.0, route.width_mm) / 2,
        )

    for region in board.regions:
        bounds = _include_points(
            bounds,
            ((point.x, point.y) for point in region.points),
        )
        for hole in region.holes:
            bounds = _include_points(
                bounds,
                ((point.x, point.y) for point in hole),
            )

    return bounds


def fit_viewport(
    board: BoardModel,
    canvas_width: float,
    canvas_height: float,
    *,
    padding: float = 30.0,
    min_scale: float = 0.05,
    max_scale: float = 100.0,
) -> tuple[float, float, float] | None:
    """Return scale and offsets that center all board evidence."""

    bounds = board_bounds(board)
    if bounds is None:
        return None

    xmin, ymin, xmax, ymax = bounds
    usable_width = max(1.0, float(canvas_width) - 2 * padding)
    usable_height = max(1.0, float(canvas_height) - 2 * padding)
    span_x = max(xmax - xmin, 1e-9)
    span_y = max(ymax - ymin, 1e-9)

    scale = min(usable_width / span_x, usable_height / span_y)
    scale = min(max_scale, max(min_scale, scale))

    drawn_width = (xmax - xmin) * scale
    drawn_height = (ymax - ymin) * scale
    offset_x = padding + (usable_width - drawn_width) / 2 - xmin * scale
    offset_y = padding + (usable_height - drawn_height) / 2 - ymin * scale
    return scale, offset_x, offset_y
