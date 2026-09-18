from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re

from ..errors import ParseError, UnsupportedFeatureError
from ..ids import stable_id
from ..models import OutlineSegment, PadCandidate, ParseDiagnostic, Point, Track
from ..provenance import Evidence, Provenance, SourceRef
from ..units import CoordinateFormat, to_mm
from .gerber_parts.step_repeat import parse_step_repeat
from .gerber_parts.tokenizer import iter_gerber_statements


_FS = re.compile(r"^%FS([LT])A?X(\d)(\d)Y(\d)(\d)\*%$")
_MO = re.compile(r"^%MO(MM|IN)\*%$")
_AD = re.compile(r"^%ADD(\d+)([CRO]),?([0-9.]+)(?:X([0-9.]+))?\*%$")
_SELECT = re.compile(r"^(?:G54)?D(\d+)\*$")
_COORD = re.compile(
    r"^(?:G0?1)?(?:X([+-]?[0-9.]+))?(?:Y([+-]?[0-9.]+))?(?:D0?([123]))?\*$"
)

_MAX_STEP_REPEAT_INSTANCES = 10_000


@dataclass(frozen=True)
class Aperture:
    code: int
    shape: str
    x: float
    y: float


@dataclass(frozen=True)
class StepRepeat:
    x_count: int
    y_count: int
    x_step_mm: float
    y_step_mm: float

    @property
    def instance_count(self) -> int:
        return self.x_count * self.y_count

    def offsets(self):
        """Yield deterministic row-major (x-fastest) repetition offsets."""
        for y_index in range(self.y_count):
            for x_index in range(self.x_count):
                yield (
                    x_index,
                    y_index,
                    x_index * self.x_step_mm,
                    y_index * self.y_step_mm,
                )


@dataclass
class GerberLayerResult:
    tracks: list[Track] = field(default_factory=list)
    pads: list[PadCandidate] = field(default_factory=list)
    outline: list[OutlineSegment] = field(default_factory=list)
    diagnostics: list[ParseDiagnostic] = field(default_factory=list)


class GerberRS274XParser:
    """Strict, auditable RS-274X subset parser.

    Supported: FS, MO, ADD(C/R/O), Dnn selection, G01/D01/D02/D03,
    G04, M02, and standard linear step-and-repeat (%SR...*% / %SR*%).

    Unsupported constructs are never silently discarded in strict mode.
    """

    def __init__(self, layer: str, strict: bool = True):
        self.layer = layer
        self.strict = strict
        self.units = "mm"
        self.xfmt = CoordinateFormat(2, 4, "L")
        self.yfmt = CoordinateFormat(2, 4, "L")
        self.apertures: dict[int, Aperture] = {}
        self.current_aperture: int | None = None
        self.current = Point(0.0, 0.0)
        self.step_repeat: StepRepeat | None = None

    def _fail_or_warn(self, path, line_no, raw, code, message, out):
        if self.strict:
            raise UnsupportedFeatureError(f"{path}:{line_no}: {message}: {raw}")
        out.diagnostics.append(
            ParseDiagnostic("warning", code, message, str(path), line_no)
        )

    def _decode(self, raw, axis):
        if raw is None:
            return None
        fmt = self.xfmt if axis == "x" else self.yfmt
        value = float(raw) if "." in raw else fmt.decode(raw)
        return to_mm(value, self.units)

    def _step_repeat_provenance(
        self,
        src: SourceRef,
        x_index: int,
        y_index: int,
        dx_mm: float,
        dy_mm: float,
    ) -> Provenance:
        prov = Provenance([src], [])
        if self.step_repeat is not None:
            prov.add_evidence(
                Evidence(
                    "gerber_step_repeat",
                    (
                        f"instance=({x_index + 1},{y_index + 1})/"
                        f"({self.step_repeat.x_count},{self.step_repeat.y_count});"
                        f" offset_mm=({dx_mm:.12g},{dy_mm:.12g})"
                    ),
                    1.0,
                    src,
                )
            )
        return prov

    def _configure_step_repeat(
        self,
        line: str,
        path: Path,
        line_no: int,
        out: GerberLayerResult,
    ) -> None:
        # Bare %SR*% terminates the active repeat block.
        if line == "%SR*%":
            self.step_repeat = None
            return

        try:
            parsed = parse_step_repeat(line)
            x_count = int(parsed["x"])
            y_count = int(parsed["y"])
            x_step_mm = to_mm(float(parsed["i"]), self.units)
            y_step_mm = to_mm(float(parsed["j"]), self.units)
        except (TypeError, ValueError, KeyError) as exc:
            self.step_repeat = None
            self._fail_or_warn(
                path,
                line_no,
                line,
                "INVALID_GERBER_STEP_REPEAT",
                f"invalid Gerber step-and-repeat ({exc})",
                out,
            )
            return

        if x_count < 1 or y_count < 1:
            self.step_repeat = None
            self._fail_or_warn(
                path,
                line_no,
                line,
                "INVALID_GERBER_STEP_REPEAT",
                "step-and-repeat counts must be positive",
                out,
            )
            return

        instance_count = x_count * y_count
        if instance_count > _MAX_STEP_REPEAT_INSTANCES:
            self.step_repeat = None
            self._fail_or_warn(
                path,
                line_no,
                line,
                "GERBER_STEP_REPEAT_LIMIT",
                (
                    f"step-and-repeat expands to {instance_count} instances; "
                    f"limit is {_MAX_STEP_REPEAT_INSTANCES}"
                ),
                out,
            )
            return

        self.step_repeat = StepRepeat(
            x_count=x_count,
            y_count=y_count,
            x_step_mm=x_step_mm,
            y_step_mm=y_step_mm,
        )

    def _iter_repetitions(self):
        if self.step_repeat is None:
            yield None, None, 0.0, 0.0
            return
        yield from self.step_repeat.offsets()

    def parse(self, path: str | Path) -> GerberLayerResult:
        p = Path(path)
        out = GerberLayerResult()

        text = p.read_text(encoding="utf-8", errors="strict")
        for line_no, line in iter_gerber_statements(text):
            if not line or line.startswith("G04"):
                continue
            if line in {"M02*", "%LPD*%"}:
                continue
            if (
                line.startswith("%TF")
                or line.startswith("%TA")
                or line.startswith("%TO")
                or line.startswith("%TD")
            ):
                out.diagnostics.append(
                    ParseDiagnostic(
                        "info",
                        "GERBER_ATTRIBUTE_PRESERVED_AS_DIAGNOSTIC",
                        line,
                        str(p),
                        line_no,
                    )
                )
                continue

            m = _FS.match(line)
            if m:
                zs, xi, xd, yi, yd = m.groups()
                self.xfmt = CoordinateFormat(int(xi), int(xd), zs)
                self.yfmt = CoordinateFormat(int(yi), int(yd), zs)
                continue

            m = _MO.match(line)
            if m:
                self.units = "mm" if m.group(1) == "MM" else "inch"
                continue

            m = _AD.match(line)
            if m:
                code, shape, a, b = m.groups()
                ax = to_mm(float(a), self.units)
                ay = to_mm(float(b), self.units) if b else ax
                self.apertures[int(code)] = Aperture(int(code), shape, ax, ay)
                continue

            m = _SELECT.match(line)
            if m and int(m.group(1)) >= 10:
                self.current_aperture = int(m.group(1))
                continue

            if line.startswith("%SR"):
                self._configure_step_repeat(line, p, line_no, out)
                continue

            if line.startswith(("G02", "G03", "G36", "G37")) or line.startswith(
                ("%AM", "%AB")
            ):
                self._fail_or_warn(
                    p,
                    line_no,
                    line,
                    "UNSUPPORTED_GERBER_CONSTRUCT",
                    "Gerber construct not implemented safely",
                    out,
                )
                continue

            m = _COORD.match(line)
            if m:
                x_raw, y_raw, op = m.groups()
                x = self._decode(x_raw, "x")
                y = self._decode(y_raw, "y")
                nxt = Point(
                    self.current.x if x is None else x,
                    self.current.y if y is None else y,
                )

                if op == "2" or op is None:
                    self.current = nxt
                    continue

                if (
                    self.current_aperture is None
                    or self.current_aperture not in self.apertures
                ):
                    raise ParseError(
                        f"{p}:{line_no}: draw/flash before valid aperture selection"
                    )

                ap = self.apertures[self.current_aperture]
                src = SourceRef(str(p), line_no, line)

                if op == "1":
                    if ap.shape != "C":
                        self._fail_or_warn(
                            p,
                            line_no,
                            line,
                            "NON_CIRCULAR_DRAW",
                            "non-circular draw aperture not modeled exactly",
                            out,
                        )
                    width = max(ap.x, ap.y)

                    for x_index, y_index, dx_mm, dy_mm in self._iter_repetitions():
                        start = Point(
                            self.current.x + dx_mm, self.current.y + dy_mm
                        )
                        end = Point(nxt.x + dx_mm, nxt.y + dy_mm)
                        if self.step_repeat is None:
                            obj_id = stable_id(
                                "trk",
                                p.name,
                                line_no,
                                self.current.x,
                                self.current.y,
                                nxt.x,
                                nxt.y,
                                width,
                                self.layer,
                            )
                        else:
                            obj_id = stable_id(
                                "trk",
                                p.name,
                                line_no,
                                self.current.x,
                                self.current.y,
                                nxt.x,
                                nxt.y,
                                width,
                                self.layer,
                                "sr",
                                x_index,
                                y_index,
                            )
                        prov = self._step_repeat_provenance(
                            src, x_index or 0, y_index or 0, dx_mm, dy_mm
                        )
                        if self.layer == "Edge.Cuts":
                            out.outline.append(
                                OutlineSegment(obj_id, start, end, prov)
                            )
                        else:
                            out.tracks.append(
                                Track(
                                    obj_id,
                                    start,
                                    end,
                                    width,
                                    self.layer,
                                    provenance=prov,
                                )
                            )

                elif op == "3":
                    for x_index, y_index, dx_mm, dy_mm in self._iter_repetitions():
                        center = Point(nxt.x + dx_mm, nxt.y + dy_mm)
                        if self.step_repeat is None:
                            obj_id = stable_id(
                                "pad",
                                p.name,
                                line_no,
                                nxt.x,
                                nxt.y,
                                ap.code,
                                self.layer,
                            )
                        else:
                            obj_id = stable_id(
                                "pad",
                                p.name,
                                line_no,
                                nxt.x,
                                nxt.y,
                                ap.code,
                                self.layer,
                                "sr",
                                x_index,
                                y_index,
                            )
                        prov = self._step_repeat_provenance(
                            src, x_index or 0, y_index or 0, dx_mm, dy_mm
                        )
                        out.pads.append(
                            PadCandidate(
                                obj_id,
                                center,
                                ap.x,
                                ap.y,
                                ap.shape,
                                self.layer,
                                provenance=prov,
                            )
                        )

                self.current = nxt
                continue

            self._fail_or_warn(
                p,
                line_no,
                line,
                "UNKNOWN_GERBER_STATEMENT",
                "unrecognized Gerber statement",
                out,
            )

        return out
