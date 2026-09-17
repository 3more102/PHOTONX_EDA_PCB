from __future__ import annotations
from dataclasses import dataclass, field
import re
from pathlib import Path
from ..errors import ParseError, UnsupportedFeatureError
from ..ids import stable_id
from ..models import Point, DrillHit, ParseDiagnostic
from ..provenance import Provenance, SourceRef
from ..units import CoordinateFormat, to_mm

_TOOL_DEF = re.compile(r"^T(\d+)C([0-9.]+)$")
_TOOL_SEL = re.compile(r"^T(\d+)$")
_HIT = re.compile(r"^(?:X([+-]?[0-9.]+))?(?:Y([+-]?[0-9.]+))?$")


@dataclass
class ExcellonResult:
    drills: list[DrillHit] = field(default_factory=list)
    diagnostics: list[ParseDiagnostic] = field(default_factory=list)


class ExcellonParser:
    """Strict point-drill parser; routed slots are rejected instead of approximated."""
    def __init__(self, strict: bool = True):
        self.strict = strict; self.units = "mm"; self.zero = "L"
        self.fmt = CoordinateFormat(2, 4, "L"); self.tools = {}; self.tool = None; self.current = Point(0.0, 0.0)

    def _decode(self, raw):
        if raw is None: return None
        value = float(raw) if "." in raw else self.fmt.decode(raw)
        return to_mm(value, self.units)

    def parse(self, path: str | Path) -> ExcellonResult:
        p = Path(path); out = ExcellonResult()
        for line_no, raw in enumerate(p.read_text(encoding="utf-8", errors="strict").splitlines(), 1):
            line = raw.strip().upper()
            if not line or line in {"M48", "%", "M30", "M95"} or line.startswith(";"): continue
            if line.startswith("METRIC"):
                self.units = "mm"; self.zero = "T" if "TZ" in line else "L"; self.fmt = CoordinateFormat(3, 3, self.zero); continue
            if line.startswith("INCH"):
                self.units = "inch"; self.zero = "T" if "TZ" in line else "L"; self.fmt = CoordinateFormat(2, 4, self.zero); continue
            if "G85" in line or line.startswith(("G00", "G01", "G02", "G03")):
                if self.strict: raise UnsupportedFeatureError(f"{p}:{line_no}: routed Excellon geometry is not implemented: {line}")
                out.diagnostics.append(ParseDiagnostic("warning", "UNSUPPORTED_EXCELLON_ROUTE", line, str(p), line_no)); continue
            m = _TOOL_DEF.match(line)
            if m:
                tool, diameter = m.groups(); self.tools[tool] = to_mm(float(diameter), self.units); continue
            m = _TOOL_SEL.match(line)
            if m: self.tool = m.group(1); continue
            m = _HIT.match(line)
            if m and (m.group(1) is not None or m.group(2) is not None):
                if self.tool is None or self.tool not in self.tools: raise ParseError(f"{p}:{line_no}: drill hit before valid tool selection")
                x = self._decode(m.group(1)); y = self._decode(m.group(2)); pt = Point(self.current.x if x is None else x, self.current.y if y is None else y)
                src = SourceRef(str(p), line_no, line); obj_id = stable_id("drill", p.name, line_no, pt.x, pt.y, self.tool)
                out.drills.append(DrillHit(obj_id, pt, self.tools[self.tool], "unknown", f"T{self.tool}", Provenance([src], []))); self.current = pt; continue
            if self.strict: raise ParseError(f"{p}:{line_no}: unrecognized Excellon statement: {line}")
            out.diagnostics.append(ParseDiagnostic("warning", "UNKNOWN_EXCELLON_STATEMENT", line, str(p), line_no))
        return out
