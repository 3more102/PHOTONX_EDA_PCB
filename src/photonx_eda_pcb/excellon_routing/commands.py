import re

from ..excellon_numeric import SIGNED_DECIMAL_PATTERN

_COORD = re.compile(
    rf"^(G00|G01)(?:X({SIGNED_DECIMAL_PATTERN}))?(?:Y({SIGNED_DECIMAL_PATTERN}))?$"
)


def parse_linear_route_command(text):
    m = _COORD.fullmatch(text.strip().upper())
    if not m:
        raise ValueError("invalid linear route command")
    return m.group(1), m.group(2), m.group(3)


def classify_route_control(text):
    s = text.strip().upper()
    if s == "M15":
        return "tool_down"
    if s in {"M16", "M17"}:
        return "tool_up"
    if s == "G05":
        return "drill_mode"
    return None
