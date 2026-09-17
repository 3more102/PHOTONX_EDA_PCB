from __future__ import annotations
from dataclasses import dataclass, field
import re
from pathlib import Path
from ..errors import ParseError, UnsupportedFeatureError
from ..ids import stable_id
from ..models import Point, Track, PadCandidate, OutlineSegment, ParseDiagnostic
from ..provenance import Provenance, SourceRef
from ..units import CoordinateFormat, to_mm

_FS = re.compile(r"^%FS([LT])A?X(\d)(\d)Y(\d)(\d)\*%$")
_MO = re.compile(r"^%MO(MM|IN)\*%$")
_AD = re.compile(r"^%ADD(\d+)([CRO]),?([0-9.]+)(?:X([0-9.]+))?\*%$")
_SELECT = re.compile(r"^(?:G54)?D(\d+)\*$")
_COORD = re.compile(r"^(?:G0?1)?(?:X([+-]?[0-9.]+))?(?:Y([+-]?[0-9.]+))?(?:D0?([123]))?\*$")


@dataclass(frozen=True)
class Aperture:
    code: int
    shape: str
    x: float
    y: float


@dataclass
class GerberLayerResult:
    tracks: list[Track] = field(default_factory=list)
    pads: list[PadCandidate] = field(default_factory=list)
    outline: list[OutlineSegment] = field(default_factory=list)
    diagnostics: list[ParseDiagnostic] = field(default_factory=list)


class GerberRS274XParser:
    """Strict, auditable RS-274X subset parser.

    Supported: FS, MO, ADD(C/R/O), Dnn selection, G01/D01/D02/D03, G04, M02.
    Unsupported constructs are never silently discarded in strict mode.
    """
    def __init__(self, layer: str, strict: bool = True):
        self.layer = layer; self.strict = strict; self.units = "mm"
        self.xfmt = CoordinateFormat(2, 4, "L"); self.yfmt = CoordinateFormat(2, 4, "L")
        self.apertures = {}; self.current_aperture = None; self.current = Point(0.0, 0.0)

    def _fail_or_warn(self, path, line_no, raw, code, message, out):
        if self.strict: raise UnsupportedFeatureError(f"{path}:{line_no}: {message}: {raw}")
        out.diagnostics.append(ParseDiagnostic("warning", code, message, str(path), line_no))

    def _decode(self, raw, axis):
        if raw is None: return None
        fmt = self.xfmt if axis == "x" else self.yfmt
        value = float(raw) if "." in raw else fmt.decode(raw)
        return to_mm(value, self.units)

    def parse(self, path: str | Path) -> GerberLayerResult:
        p = Path(path); out = GerberLayerResult()
        for line_no, raw in enumerate(p.read_text(encoding="utf-8", errors="strict").splitlines(), 1):
            line = raw.strip()
            if not line or line.startswith("G04"): continue
            if line in {"M02*", "%LPD*%"}: continue
            if line.startswith("%TF") or line.startswith("%TA") or line.startswith("%TO") or line.startswith("%TD"):
                out.diagnostics.append(ParseDiagnostic("info", "GERBER_ATTRIBUTE_PRESERVED_AS_DIAGNOSTIC", line, str(p), line_no)); continue
            m = _FS.match(line)
            if m:
                zs, xi, xd, yi, yd = m.groups(); self.xfmt = CoordinateFormat(int(xi), int(xd), zs); self.yfmt = CoordinateFormat(int(yi), int(yd), zs); continue
            m = _MO.match(line)
            if m: self.units = "mm" if m.group(1) == "MM" else "inch"; continue
            m = _AD.match(line)
            if m:
                code, shape, a, b = m.groups(); ax = to_mm(float(a), self.units); ay = to_mm(float(b), self.units) if b else ax
                self.apertures[int(code)] = Aperture(int(code), shape, ax, ay); continue
            m = _SELECT.match(line)
            if m and int(m.group(1)) >= 10: self.current_aperture = int(m.group(1)); continue
            if line.startswith(("G02", "G03", "G36", "G37")) or line.startswith("%AM") or line.startswith("%SR") or line.startswith("%AB"):
                self._fail_or_warn(p, line_no, line, "UNSUPPORTED_GERBER_CONSTRUCT", "Gerber construct not implemented safely", out); continue
            m = _COORD.match(line)
            if m:
                x_raw, y_raw, op = m.groups(); x = self._decode(x_raw, "x"); y = self._decode(y_raw, "y")
                nxt = Point(self.current.x if x is None else x, self.current.y if y is None else y)
                if op == "2" or op is None: self.current = nxt; continue
                if self.current_aperture is None or self.current_aperture not in self.apertures: raise ParseError(f"{p}:{line_no}: draw/flash before valid aperture selection")
                ap = self.apertures[self.current_aperture]; src = SourceRef(str(p), line_no, line)
                if op == "1":
                    if ap.shape != "C": self._fail_or_warn(p, line_no, line, "NON_CIRCULAR_DRAW", "non-circular draw aperture not modeled exactly", out)
                    width = max(ap.x, ap.y); obj_id = stable_id("trk", p.name, line_no, self.current.x, self.current.y, nxt.x, nxt.y, width, self.layer); prov = Provenance([src], [])
                    if self.layer == "Edge.Cuts": out.outline.append(OutlineSegment(obj_id, self.current, nxt, prov))
                    else: out.tracks.append(Track(obj_id, self.current, nxt, width, self.layer, provenance=prov))
                elif op == "3":
                    obj_id = stable_id("pad", p.name, line_no, nxt.x, nxt.y, ap.code, self.layer); prov = Provenance([src], [])
                    out.pads.append(PadCandidate(obj_id, nxt, ap.x, ap.y, ap.shape, self.layer, provenance=prov))
                self.current = nxt; continue
            self._fail_or_warn(p, line_no, line, "UNKNOWN_GERBER_STATEMENT", "unrecognized Gerber statement", out)
        return out
