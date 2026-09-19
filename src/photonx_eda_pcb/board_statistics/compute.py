from .model import BoardStats
from ..excellon_routing.measure import route_length_mm
from ..geometry.measure import total_outline_length, total_track_length


def compute_board_stats(board):
    points = []
    for segment in board.outline:
        points.extend(
            [
                (float(segment.start.x), float(segment.start.y)),
                (float(segment.end.x), float(segment.end.y)),
            ]
        )

    if points:
        xs = [point[0] for point in points]
        ys = [point[1] for point in points]
        width = max(xs) - min(xs)
        height = max(ys) - min(ys)
    else:
        width = height = None

    routes = getattr(board, "routes", ())
    return BoardStats(
        tracks=len(board.tracks),
        pads=len(board.pads),
        drills=len(board.drills),
        outline_segments=len(board.outline),
        nets=len(board.nets),
        components=len(board.components),
        total_track_length_mm=round(total_track_length(board), 6),
        board_width_mm=None if width is None else round(width, 6),
        board_height_mm=None if height is None else round(height, 6),
        slots=len(getattr(board, "slots", ())),
        routes=len(routes),
        regions=len(getattr(board, "regions", ())),
        diagnostics=len(getattr(board, "diagnostics", ())),
        route_length_mm=round(sum(route_length_mm(route) for route in routes), 6),
        outline_length_mm=round(total_outline_length(board), 6),
    )
