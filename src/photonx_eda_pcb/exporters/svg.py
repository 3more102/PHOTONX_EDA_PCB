from html import escape
from pathlib import Path

from ..geometry.bbox import board_bounds


def _attr(value: object) -> str:
    return escape(str(value), quote=True)


def _object_attrs(obj, kind: str, *, layer: str | None = None) -> str:
    attrs = [
        f'class="{kind}"',
        f'data-object-id="{_attr(obj.id)}"',
    ]
    if layer is not None:
        attrs.append(f'data-layer="{_attr(layer)}"')
    net_id = getattr(obj, "net_id", None)
    if net_id is not None:
        attrs.append(f'data-net-id="{_attr(net_id)}"')
    return " ".join(attrs)


def _region_path(region) -> str:
    rings = [region.points, *region.holes]
    commands: list[str] = []
    for ring in rings:
        if len(ring) < 3:
            continue
        commands.append(
            "M "
            + " L ".join(f"{point.x},{point.y}" for point in ring)
            + " Z"
        )
    return " ".join(commands)


def export_svg(board, path: str | Path, padding: float = 2.0) -> Path:
    """Export an evidence-review SVG covering all physical BoardModel families."""

    bounds = board_bounds(board)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if bounds is None:
        path.write_text('<svg xmlns="http://www.w3.org/2000/svg"/>\n', encoding="utf-8")
        return path

    width = bounds.width + 2 * padding
    height = bounds.height + 2 * padding
    origin_x = bounds.min_x - padding
    origin_y = bounds.min_y - padding
    lines = [
        (
            '<svg xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="{origin_x} {origin_y} {width} {height}">'
        )
    ]

    for region in board.regions:
        path_data = _region_path(region)
        if path_data:
            lines.append(
                f'<path {_object_attrs(region, "copper-region", layer=region.layer)} '
                f'd="{path_data}" fill="black" fill-opacity="0.15" '
                'stroke="black" fill-rule="evenodd"/>'
            )

    for track in board.tracks:
        lines.append(
            f'<line {_object_attrs(track, "track", layer=track.layer)} '
            f'x1="{track.start.x}" y1="{track.start.y}" '
            f'x2="{track.end.x}" y2="{track.end.y}" '
            f'stroke="black" stroke-width="{track.width}" stroke-linecap="round"/>'
        )

    for pad in board.pads:
        attrs = _object_attrs(pad, "pad", layer=pad.layer)
        if pad.shape.upper() == "C":
            lines.append(
                f'<ellipse {attrs} cx="{pad.center.x}" cy="{pad.center.y}" '
                f'rx="{pad.size_x / 2.0}" ry="{pad.size_y / 2.0}" '
                'fill="none" stroke="black"/>'
            )
        else:
            radius = min(pad.size_x, pad.size_y) / 2.0 if pad.shape.upper() == "O" else 0
            lines.append(
                f'<rect {attrs} x="{pad.center.x - pad.size_x / 2.0}" '
                f'y="{pad.center.y - pad.size_y / 2.0}" '
                f'width="{pad.size_x}" height="{pad.size_y}" '
                f'rx="{radius}" ry="{radius}" fill="none" stroke="black"/>'
            )

    for drill in board.drills:
        lines.append(
            f'<circle {_object_attrs(drill, "drill")} '
            f'cx="{drill.center.x}" cy="{drill.center.y}" '
            f'r="{drill.diameter / 2.0}" fill="none" stroke="black"/>'
        )

    for slot in board.slots:
        lines.append(
            f'<line {_object_attrs(slot, "slot")} '
            f'x1="{slot.start[0]}" y1="{slot.start[1]}" '
            f'x2="{slot.end[0]}" y2="{slot.end[1]}" '
            f'stroke="black" stroke-width="{slot.width_mm}" stroke-linecap="round"/>'
        )

    for route in board.routes:
        if not route.points:
            continue
        point_text = " ".join(f"{x},{y}" for x, y in route.points)
        lines.append(
            f'<polyline {_object_attrs(route, "route")} points="{point_text}" '
            f'fill="none" stroke="black" stroke-width="{route.width_mm}" '
            'stroke-linecap="round" stroke-linejoin="round"/>'
        )

    for segment in board.outline:
        lines.append(
            f'<line {_object_attrs(segment, "outline")} '
            f'x1="{segment.start.x}" y1="{segment.start.y}" '
            f'x2="{segment.end.x}" y2="{segment.end.y}" '
            'fill="none" stroke="black" vector-effect="non-scaling-stroke"/>'
        )

    lines.append("</svg>")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
