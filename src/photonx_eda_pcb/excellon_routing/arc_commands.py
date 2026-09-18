from __future__ import annotations

import re


_ARC_ROUTE = re.compile(
    r"^(G02|G03)"
    r"(?:X([+-]?[0-9.]+))?"
    r"(?:Y([+-]?[0-9.]+))?"
    r"(?:I([+-]?[0-9.]+))?"
    r"(?:J([+-]?[0-9.]+))?$"
)


def parse_arc_route_command(text: str):
    """Parse the supported Excellon routed-arc subset.

    PHOTONX accepts G02/G03 with optional X/Y endpoint coordinates and I/J
    center offsets. Radius/A-form arcs intentionally remain outside this
    parser because their dialect semantics vary between CAM generators.
    """
    match = _ARC_ROUTE.fullmatch(text.strip().upper())
    if not match:
        raise ValueError("invalid Excellon routed-arc command")
    return match.groups()
