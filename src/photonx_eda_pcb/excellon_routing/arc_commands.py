from __future__ import annotations

import re


_ARC_ROUTE = re.compile(
    r"^(G02|G03)"
    r"(?:X([+-]?[0-9.]+))?"
    r"(?:Y([+-]?[0-9.]+))?"
    r"(?:I([+-]?[0-9.]+))?"
    r"(?:J([+-]?[0-9.]+))?$"
)

_RADIUS_ARC_ROUTE = re.compile(
    r"^(G02|G03)"
    r"X([+-]?[0-9.]+)"
    r"Y([+-]?[0-9.]+)"
    r"A([0-9.]+)$"
)


def parse_arc_route_command(text: str):
    """Parse the supported Excellon routed-arc subset.

    PHOTONX accepts G02/G03 with optional X/Y endpoint coordinates and I/J
    center offsets. The separate radius parser below handles the standard
    XNC X/Y/A form without broadening this helper's existing tuple API.
    """
    match = _ARC_ROUTE.fullmatch(text.strip().upper())
    if not match:
        raise ValueError("invalid Excellon routed-arc command")
    return match.groups()


def parse_radius_arc_route_command(text: str):
    """Parse the standard XNC radius-form routed-arc command.

    XNC defines G02/G03 circular routing as X/Y endpoint coordinates plus a
    positive A radius. Both endpoint coordinates are required by this bounded
    production parser.
    """
    match = _RADIUS_ARC_ROUTE.fullmatch(text.strip().upper())
    if not match:
        raise ValueError("invalid XNC radius routed-arc command")
    return match.groups()
