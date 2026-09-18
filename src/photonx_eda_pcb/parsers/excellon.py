from __future__ import annotations
from dataclasses import dataclass, field
from math import hypot, pi, sqrt
import re
from pathlib import Path
from ..errors import ParseError, UnsupportedFeatureError
from ..gerber_geometry.arc import (
    ArcSpec,
    arc_points,
    segments_for_chord_error,
    sweep_radians,
    validate_arc,
)
from ..gerber_geometry.model import GeoPoint
from ..ids import stable_id
from ..models import Point, DrillHit, ParseDiagnostic
from ..mechanical_features.model import SlotFeature
from ..excellon_routing.model import RoutedPath
from ..excellon_routing.state import LinearRouteState
from ..excellon_routing.commands import parse_linear_route_command,classify_route_control
from ..excellon_routing.arc_commands import (
    parse_arc_route_command,
    parse_radius_arc_route_command,
)
from ..provenance import Evidence, Provenance, SourceRef
from ..units import CoordinateFormat, to_mm
from .excellon_parts.slots import parse_slot_command

_TOOL_DEF = re.compile(r"^T(\d+)C([0-9.]+)(?:F[0-9.]+)?(?:S[0-9.]+)?$")
_TOOL_SEL = re.compile(r"^T(\d+)$")
_HIT = re.compile(r"^(?:X([+-]?[0-9.]+))?(?:Y([+-]?[0-9.]+))?$")

_ROUTE_ARC_MAX_CHORD_ERROR_MM = 0.005
_ROUTE_ARC_MAX_SEGMENTS = 4096

@dataclass
class ExcellonResult:
    drills: list[DrillHit] = field(default_factory=list)
    slots: list[SlotFeature] = field(default_factory=list)
    routes: list[RoutedPath] = field(default_factory=list)
    diagnostics: list[ParseDiagnostic] = field(default_factory=list)

class ExcellonParser:
    """Strict point-drill/G85 parser with conservative linear route support.

    Supported route sequence: G00 position -> M15 -> G01 and/or bounded
    G02/G03 circular interpolation -> M16/M17. Routed arcs support the
    existing I/J center-offset subset plus standard XNC X/Y/A radius form,
    and are converted to deterministic polyline points with explicit evidence.
    """
    def __init__(self, strict: bool = True):
        self.strict = strict; self.units = "mm"; self.zero = "L"; self.units_declared = False
        self.fmt = CoordinateFormat(2, 4, "L"); self.tools = {}; self.tool = None; self.current = Point(0.0, 0.0)
        self.route=LinearRouteState();self._route_sources=[];self._route_evidence=[]
        self.geometry_enabled=True

    def _disable_geometry(self,out:ExcellonResult):
        self.geometry_enabled=False
        out.drills.clear();out.slots.clear();out.routes.clear()
        self.route=LinearRouteState();self._route_sources=[];self._route_evidence=[]

    def _decode(self, raw):
        if raw is None:return None
        value=float(raw) if "." in raw else self.fmt.decode(raw)
        return to_mm(value,self.units)

    def _route_xy(self,xraw,yraw):
        x=self._decode(xraw);y=self._decode(yraw)
        return (self.current.x if x is None else x,self.current.y if y is None else y)

    def _route_arc_tolerance_mm(self):
        # Keep tolerance below one coordinate grid step so very small but
        # valid routed arcs are not mistaken for zero-radius geometry.
        resolution = to_mm(10 ** (-self.fmt.decimal), self.units)
        return max(1e-9, 0.25 * resolution)

    def _resolve_radius_arc_center(self, x, y, radius, clockwise):
        """Resolve the unique <=180-degree center for standard XNC A-radius arcs."""
        tolerance = self._route_arc_tolerance_mm()
        if radius <= tolerance:
            raise ValueError("radius-form arc radius must be positive")

        dx = x - self.current.x
        dy = y - self.current.y
        chord = hypot(dx, dy)
        if chord <= tolerance:
            raise ValueError(
                "radius-form arc start/end points coincide; center is indeterminate"
            )
        if chord > (2.0 * radius) + tolerance:
            raise ValueError(
                f"arc chord {chord:.12g} exceeds diameter {2.0 * radius:.12g}"
            )

        midpoint_x = (self.current.x + x) / 2.0
        midpoint_y = (self.current.y + y) / 2.0
        half_chord = chord / 2.0
        h_sq = radius * radius - half_chord * half_chord
        if h_sq < 0.0:
            # Allow only the coordinate-resolution rounding already admitted
            # by the chord-vs-diameter tolerance above.
            h_sq = 0.0
        height = sqrt(h_sq)
        perp_x = -dy / chord
        perp_y = dx / chord

        candidates = []
        seen = set()
        for sign in (-1.0, 1.0):
            center = (
                midpoint_x + sign * height * perp_x,
                midpoint_y + sign * height * perp_y,
            )
            key = (round(center[0], 15), round(center[1], 15))
            if key in seen:
                continue
            seen.add(key)
            spec = ArcSpec(
                GeoPoint(self.current.x, self.current.y),
                GeoPoint(x, y),
                GeoPoint(center[0], center[1]),
                clockwise=clockwise,
            )
            try:
                validate_arc(spec, rel_tol=1e-6, abs_tol=tolerance)
                sweep = abs(
                    sweep_radians(spec, rel_tol=1e-6, abs_tol=tolerance)
                )
            except ValueError:
                continue
            if sweep <= pi + 1e-9:
                candidates.append((sweep, center))

        if len(candidates) != 1:
            raise ValueError(
                "radius-form arc does not resolve to one <=180-degree center"
            )
        return candidates[0][1]

    def _route_arc(self,p,out,line_no,line):
        encoding="ij"
        araw=None
        try:
            command,xraw,yraw,iraw,jraw=parse_arc_route_command(line)
        except ValueError:
            try:
                command,xraw,yraw,araw=parse_radius_arc_route_command(line)
                iraw=jraw=None
                encoding="radius"
            except ValueError:
                if self.strict:
                    raise UnsupportedFeatureError(
                        f"{p}:{line_no}: unsupported Excellon routed-arc syntax: {line}"
                    )
                out.diagnostics.append(
                    ParseDiagnostic(
                        "warning",
                        "UNSUPPORTED_EXCELLON_ROUTE_ARC_SYNTAX",
                        line,
                        str(p),
                        line_no,
                    )
                )
                return

        if not self.route.tool_down:
            message="routed arc requires G00/M15 before G02/G03"
            if self.strict:raise UnsupportedFeatureError(f"{p}:{line_no}: {message}")
            out.diagnostics.append(ParseDiagnostic("warning","UNSUPPORTED_EXCELLON_ROUTE_SEQUENCE",message,str(p),line_no));return

        if self.tool is None or self.tool not in self.tools:
            raise ParseError(f"{p}:{line_no}: routed arc before valid tool selection")

        x,y=self._route_xy(xraw,yraw)
        tolerance=self._route_arc_tolerance_mm()

        try:
            if encoding=="ij":
                if iraw is None and jraw is None:
                    message="G02/G03 I/J routed arc requires center offsets"
                    if self.strict:raise UnsupportedFeatureError(f"{p}:{line_no}: {message}")
                    out.diagnostics.append(ParseDiagnostic("warning","UNSUPPORTED_EXCELLON_ROUTE_ARC_CENTER",message,str(p),line_no));return
                i=0.0 if iraw is None else self._decode(iraw)
                j=0.0 if jraw is None else self._decode(jraw)
                center=(self.current.x+i,self.current.y+j)
            else:
                declared_radius=self._decode(araw)
                center=self._resolve_radius_arc_center(
                    x,
                    y,
                    declared_radius,
                    clockwise=command=="G02",
                )

            spec=ArcSpec(
                GeoPoint(self.current.x,self.current.y),
                GeoPoint(x,y),
                GeoPoint(center[0],center[1]),
                clockwise=command=="G02",
            )
            radius=validate_arc(spec,rel_tol=1e-6,abs_tol=tolerance)
            segment_count=segments_for_chord_error(
                spec,
                _ROUTE_ARC_MAX_CHORD_ERROR_MM,
                max_segments=_ROUTE_ARC_MAX_SEGMENTS,
                rel_tol=1e-6,
                abs_tol=tolerance,
            )
            points=arc_points(
                spec,
                segments=segment_count,
                rel_tol=1e-6,
                abs_tol=tolerance,
            )
        except ValueError as exc:
            message=f"invalid Excellon routed arc ({exc})"
            if self.strict:raise ParseError(f"{p}:{line_no}: {message}: {line}")
            out.diagnostics.append(ParseDiagnostic("warning","EXCELLON_ROUTE_ARC_INVALID",message,str(p),line_no));return

        try:
            for point in points[1:]:
                self.route.line(point.x,point.y)
        except RuntimeError as exc:
            if self.strict:raise ParseError(f"{p}:{line_no}: {exc}")
            out.diagnostics.append(ParseDiagnostic("warning","EXCELLON_ROUTE_STATE",str(exc),str(p),line_no));return

        src=SourceRef(str(p),line_no,line)
        self._route_sources.append(src)
        self._route_evidence.append(
            Evidence(
                "excellon_route_arc_tessellation",
                (
                    f"encoding={encoding}; "
                    f"direction={'CW' if command=='G02' else 'CCW'}; "
                    f"center_mm=({center[0]:.12g},{center[1]:.12g}); "
                    f"radius_mm={radius:.12g}; segments={segment_count}; "
                    f"max_chord_error_mm={_ROUTE_ARC_MAX_CHORD_ERROR_MM:.12g}"
                ),
                1.0,
                src,
            )
        )
        self.current=Point(x,y)

    def _finish_route(self,p,out,line_no,line):
        try:pts=self.route.raise_tool()
        except RuntimeError as exc:
            if self.strict:raise ParseError(f"{p}:{line_no}: {exc}")
            out.diagnostics.append(ParseDiagnostic("warning","EXCELLON_ROUTE_STATE",str(exc),str(p),line_no));return
        if len(pts)<2:
            if self.strict:raise ParseError(f"{p}:{line_no}: routed path has no linear segment")
            out.diagnostics.append(ParseDiagnostic("warning","EXCELLON_ROUTE_EMPTY","route ended without a segment",str(p),line_no));return
        if self.tool is None or self.tool not in self.tools:raise ParseError(f"{p}:{line_no}: route before valid tool selection")
        rid=stable_id("route",p.name,pts,self.tool,self.tools[self.tool])
        prov=Provenance(list(self._route_sources),list(self._route_evidence))
        out.routes.append(RoutedPath(rid,pts,self.tools[self.tool],"unknown",f"T{self.tool}",prov))
        self._route_sources=[];self._route_evidence=[]

    def parse(self,path:str|Path)->ExcellonResult:
        p=Path(path);out=ExcellonResult()
        for line_no,raw in enumerate(p.read_text(encoding="utf-8-sig",errors="strict").splitlines(),1):
            line=raw.strip().upper()
            if not line or line in {"M48","%","M30","M95"} or line.startswith(";"):continue
            if line.startswith("METRIC") or line == "M71":
                self.units="mm";self.units_declared=True;self.zero="T" if "TZ" in line else "L";self.fmt=CoordinateFormat(3,3,self.zero);continue
            if line.startswith("INCH") or line == "M72":
                self.units="inch";self.units_declared=True;self.zero="T" if "TZ" in line else "L";self.fmt=CoordinateFormat(2,4,self.zero);continue
            if line.startswith(("FMAT,", "VER,")):
                continue
            if line == "G90":
                continue
            if line == "G91":
                if self.strict:raise UnsupportedFeatureError(f"{p}:{line_no}: incremental Excellon coordinates are unsupported: {line}")
                out.diagnostics.append(ParseDiagnostic("warning","UNSUPPORTED_EXCELLON_INCREMENTAL",line,str(p),line_no))
                self._disable_geometry(out)
                continue
            if line.startswith("ICI,"):
                if line == "ICI,OFF":
                    continue
                if self.strict:raise UnsupportedFeatureError(f"{p}:{line_no}: incremental Excellon coordinates are unsupported: {line}")
                out.diagnostics.append(ParseDiagnostic("warning","UNSUPPORTED_EXCELLON_INCREMENTAL",line,str(p),line_no))
                self._disable_geometry(out)
                continue
            if not self.geometry_enabled:
                continue
            if "G85" in line:
                if self.route.tool_down:
                    if self.strict:raise ParseError(f"{p}:{line_no}: G85 encountered while route tool is down")
                    out.diagnostics.append(ParseDiagnostic("warning","EXCELLON_ROUTE_STATE","G85 while route active",str(p),line_no));continue
                try:x1r,y1r,x2r,y2r=parse_slot_command(line)
                except ValueError:
                    if self.strict:raise UnsupportedFeatureError(f"{p}:{line_no}: unsupported Excellon G85 slot syntax: {line}")
                    out.diagnostics.append(ParseDiagnostic("warning","UNSUPPORTED_EXCELLON_SLOT",line,str(p),line_no));continue
                if self.tool is None or self.tool not in self.tools:raise ParseError(f"{p}:{line_no}: slot before valid tool selection")
                x1,y1,x2,y2=(self._decode(v) for v in (x1r,y1r,x2r,y2r))
                src=SourceRef(str(p),line_no,line);slot_id=stable_id("slot",p.name,line_no,x1,y1,x2,y2,self.tool)
                out.slots.append(SlotFeature(slot_id,(x1,y1),(x2,y2),self.tools[self.tool],"unknown",f"T{self.tool}",Provenance([src],[])))
                self.current=Point(x2,y2);continue
            if line.startswith(("G02","G03")):
                self._route_arc(p,out,line_no,line);continue
            if line.startswith(("G00","G01")):
                cmd, xraw, yraw = None, None, None
                try:cmd,xraw,yraw=parse_linear_route_command(line)
                except ValueError:
                    if self.strict:raise ParseError(f"{p}:{line_no}: malformed linear route command: {line}")
                    out.diagnostics.append(ParseDiagnostic("warning","MALFORMED_EXCELLON_ROUTE",line,str(p),line_no));continue
                x,y=self._route_xy(xraw,yraw);src=SourceRef(str(p),line_no,line)
                if cmd=="G00":
                    try:self.route.position(x,y)
                    except RuntimeError as exc:
                        if self.strict:raise ParseError(f"{p}:{line_no}: {exc}")
                        out.diagnostics.append(ParseDiagnostic("warning","EXCELLON_ROUTE_STATE",str(exc),str(p),line_no));continue
                    self.current=Point(x,y);self._route_sources=[src];self._route_evidence=[];continue
                if self.tool is None or self.tool not in self.tools:raise ParseError(f"{p}:{line_no}: linear route before valid tool selection")
                if not self.route.tool_down:
                    if self.strict:raise UnsupportedFeatureError(f"{p}:{line_no}: standalone G01 routing is unsupported; use G00/M15/G01/M16 sequence")
                    out.diagnostics.append(ParseDiagnostic("warning","UNSUPPORTED_EXCELLON_ROUTE_SEQUENCE",line,str(p),line_no));continue
                try:self.route.line(x,y)
                except RuntimeError as exc:
                    if self.strict:raise ParseError(f"{p}:{line_no}: {exc}")
                    out.diagnostics.append(ParseDiagnostic("warning","EXCELLON_ROUTE_STATE",str(exc),str(p),line_no));continue
                self.current=Point(x,y);self._route_sources.append(src);continue
            control=classify_route_control(line)
            if control=="tool_down":
                if self.tool is None or self.tool not in self.tools:raise ParseError(f"{p}:{line_no}: M15 before valid tool selection")
                try:self.route.lower()
                except RuntimeError as exc:
                    if self.strict:raise ParseError(f"{p}:{line_no}: {exc}")
                    out.diagnostics.append(ParseDiagnostic("warning","EXCELLON_ROUTE_STATE",str(exc),str(p),line_no));continue
                self._route_sources.append(SourceRef(str(p),line_no,line));continue
            if control=="tool_up":
                self._route_sources.append(SourceRef(str(p),line_no,line));self._finish_route(p,out,line_no,line);continue
            if control=="drill_mode":
                if self.route.tool_down:
                    if self.strict:raise ParseError(f"{p}:{line_no}: G05 while route tool is down")
                    out.diagnostics.append(ParseDiagnostic("warning","EXCELLON_ROUTE_STATE","G05 while route active",str(p),line_no));continue
                continue
            m=_TOOL_DEF.match(line)
            if m:
                if not self.units_declared:
                    message = "tool diameter encountered before explicit METRIC/INCH/M71/M72 units"
                    if self.strict:
                        raise ParseError(f"{p}:{line_no}: {message}")
                    out.diagnostics.append(
                        ParseDiagnostic(
                            "warning",
                            "EXCELLON_UNITS_UNDECLARED",
                            message,
                            str(p),
                            line_no,
                        )
                    )
                    self._disable_geometry(out)
                    continue
                tool,diameter=m.groups()
                diameter_value=float(diameter)
                if diameter_value <= 0:
                    message="Excellon tool diameter must be positive"
                    if self.strict:
                        raise ParseError(f"{p}:{line_no}: {message}: {line}")
                    out.diagnostics.append(
                        ParseDiagnostic(
                            "warning",
                            "INVALID_EXCELLON_TOOL_DIAMETER",
                            message,
                            str(p),
                            line_no,
                        )
                    )
                    self._disable_geometry(out)
                    continue
                self.tools[tool]=to_mm(diameter_value,self.units);continue
            m=_TOOL_SEL.match(line)
            if m:
                if self.route.tool_down:
                    if self.strict:raise ParseError(f"{p}:{line_no}: tool change while route tool is down")
                    out.diagnostics.append(ParseDiagnostic("warning","EXCELLON_ROUTE_STATE","tool change while route active",str(p),line_no));continue
                self.tool=m.group(1);continue
            m=_HIT.match(line)
            if m and (m.group(1) is not None or m.group(2) is not None):
                if self.route.tool_down:
                    if self.strict:raise ParseError(f"{p}:{line_no}: drill hit while route tool is down")
                    out.diagnostics.append(ParseDiagnostic("warning","EXCELLON_ROUTE_STATE","drill hit while route active",str(p),line_no));continue
                if self.tool is None or self.tool not in self.tools:raise ParseError(f"{p}:{line_no}: drill hit before valid tool selection")
                x=self._decode(m.group(1));y=self._decode(m.group(2));pt=Point(self.current.x if x is None else x,self.current.y if y is None else y)
                src=SourceRef(str(p),line_no,line);obj_id=stable_id("drill",p.name,line_no,pt.x,pt.y,self.tool)
                out.drills.append(DrillHit(obj_id,pt,self.tools[self.tool],"unknown",f"T{self.tool}",Provenance([src],[])));self.current=pt;continue
            if self.strict:raise ParseError(f"{p}:{line_no}: unrecognized Excellon statement: {line}")
            out.diagnostics.append(ParseDiagnostic("warning","UNKNOWN_EXCELLON_STATEMENT",line,str(p),line_no))
        if self.route.tool_down:
            if self.strict:raise ParseError(f"{p}: EOF while route tool is down")
            out.diagnostics.append(ParseDiagnostic("warning","EXCELLON_ROUTE_UNTERMINATED","EOF while route tool is down",str(p),None))
        return out
