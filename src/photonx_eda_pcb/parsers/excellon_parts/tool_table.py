import re
from dataclasses import dataclass

from ...excellon_numeric import UNSIGNED_DECIMAL_PATTERN

_RE = re.compile(rf"T(?P<tool>\d+)(?:C(?P<diam>{UNSIGNED_DECIMAL_PATTERN}))?")


@dataclass(frozen=True)
class DrillTool:
    number: int
    diameter: float | None = None


def parse_tool_definition(text: str) -> DrillTool:
    m = _RE.fullmatch(text.strip())
    if not m:
        raise ValueError("invalid tool definition")
    return DrillTool(int(m["tool"]), float(m["diam"]) if m["diam"] else None)
