from __future__ import annotations

import re


_ARC_ROUTE = re.compile(
    r"^(G02|G03)"
    r"(?:X([+-]?[0-9.]+))?"
    r"(?:Y([+-]?[0-9.]+))?"
    r"(?:I([+-]?[0-9.]+))?"
    r"(?:J([+-]?[0-9.]+))?"
    r"(?:A([+-]?[0-9.]+))?$"
)


def parse_arc_route_command(text: str):
    """Parse the supported Excellon routed-arc subset.

    PHOTONX accepts G02/G03 with optional X/Y endpoint coordinates and either
    I/J center offsets or an inline A# radius. Higher-order/modal radius
    dialects remain outside this parser and must fail closed.
    """
    match = _ARC_ROUTE.fullmatch(text.strip().upper())
    if not match:
        raise ValueError("invalid Excellon routed-arc command")
    return match.groups()
