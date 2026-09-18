from __future__ import annotations

from dataclasses import dataclass, field
from math import isclose, pi
from pathlib import Path
import re

from ..aperture_macros import evaluate_macro, parse_macro_body
from ..errors import ParseError, UnsupportedFeatureError
from ..gerber_geometry.arc import (
    ArcSpec,
    arc_points,
    arc_radii,
    segments_for_chord_error,
    sweep_radians,
    validate_arc,
)
from ..gerber_geometry.model import GeoPoint
from ..ids import stable_id
from ..models import OutlineSegment, PadCandidate, ParseDiagnostic, Point, Track
from ..provenance import Evidence, Provenance, SourceRef
from ..units import CoordinateFormat, to_mm
from .gerber_parts.step_repeat import parse_step_repeat
from .gerber_parts.tokenizer import iter_gerber_statements


_FS = re.compile(r"^%FS([LT])A?X(\d)(\d)Y(\d)(\d)\*%$")
_MO = re.compile(r"^%MO(MM|IN)\*%$")
_AD_STANDARD = re.compile(
    r"^%ADD(\d+)([CRO]),?([0-9.]+(?:X[0-9.]+)*)\*%$"
)
_AD_MACRO = re.compile(r"^%ADD(\d+)([A-Za-z_.$][A-Za-z0-9_.$-]*)(?:,([^*]*))?\*%$")
_SELECT = re.compile(r"^(?:G54)?D(\d+)\*$")
_OP_SELECT = re.compile(r"^D0?([123])\*$")
_COORD = re.compile(
    r"^(?:G0?1)?(?:X([+-]?[0-9.]+))?(?:Y([+-]?[0-9.]+))?(?:D0?([123]))?\*$"
)
_ARC_COORD = re.compile(
    r"^(?:(G0?[23]))?"
    r"(?:X([+-]?[0-9.]+))?"
    r"(?:Y([+-]?[0-9.]+))?"
    r"(?:I([+-]?[0-9.]+))?"
    r"(?:J([+-]?[0-9.]+))?"
    r"(?:D0?([12]))?\*$"
)
_FILE_POLARITY = re.compile(
    r"^%TF\.FilePolarity,(Positive|Negative)\*%$",
    re.IGNORECASE,
)
_LAYER_POLARITY = re.compile(r"^%LP([CD])\*%$", re.IGNORECASE)
_APERTURE_MIRROR = re.compile(r"^%LM(N|X|Y|XY)\*%$", re.IGNORECASE)
_APERTURE_ROTATION = re.compile(
    r"^%LR([+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+))\*%$",
    re.IGNORECASE,
)
_APERTURE_SCALING = re.compile(
    r"^%LS([+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+))\*%$",
    re.IGNORECASE,
)

_MAX_STEP_REPEAT_INSTANCES = 10_000
_ARC_MAX_CHORD_ERROR_MM = 0.005
_MAX_ARC_SEGMENTS = 4096


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
    bounded G74 single-quadrant and G75 multi-quadrant G02/G03 circular
    interpolation with circular apertures, G04, M02, and standard linear
    step-and-repeat (%SR...*% / %SR*%).

    Unsupported constructs are never silently discarded in strict mode.
    """

    def __init__(self, layer: str, strict: bool = True):
        self.layer = layer
        self.strict = strict
        self.units = "mm"
        self.xfmt = CoordinateFormat(2, 4, "L")
        self.yfmt = CoordinateFormat(2, 4, "L")
        self.apertures: dict[int, Aperture] = {}
        self.aperture_macros: dict[str, str] = {}
        self.unsupported_apertures: set[int] = set()
        self.current_aperture: int | None = None
        self.current = Point(0.0, 0.0)
        self.step_repeat: StepRepeat | None = None
        self.interpolation = "linear"
        self.quadrant_mode: str | None = None
        self.current_operation: str | None = None
        self.file_polarity: str | None = None
        self.layer_polarity = "dark"
        self.image_geometry_enabled = True

    def _fail_or_warn(self, path, line_no, raw, code, message, out):
        if self.strict:
            raise UnsupportedFeatureError(f"{path}:{line_no}: {message}: {raw}")
        out.diagnostics.append(
            ParseDiagnostic("warning", code, message, str(path), line_no)
        )

    def _disable_image_geometry(self, out: GerberLayerResult) -> None:
        """Prevent unsupported file-image semantics from leaking geometry."""
        self.image_geometry_enabled = False
        out.tracks.clear()
        out.pads.clear()
        out.outline.clear()

    def _handle_file_polarity(
        self,
        line: str,
        path: Path,
        line_no: int,
        out: GerberLayerResult,
    ) -> None:
        match = _FILE_POLARITY.match(line)
        if match is None:
            self._parse_error_or_warn(
                path,
                line_no,
                line,
                "INVALID_GERBER_FILE_POLARITY",
                "invalid X2 .FilePolarity attribute",
                out,
            )
            if not self.strict:
                self._disable_image_geometry(out)
            return

        polarity = match.group(1).lower()
        if self.file_polarity is not None and self.file_polarity != polarity:
            self._fail_or_warn(
                path,
                line_no,
                line,
                "CONFLICTING_GERBER_FILE_POLARITY",
                (
                    "conflicting X2 .FilePolarity values are not modeled safely "
                    f"({self.file_polarity} -> {polarity})"
                ),
                out,
            )
            if not self.strict:
                self._disable_image_geometry(out)
            return

        self.file_polarity = polarity
        if polarity == "negative":
            self._fail_or_warn(
                path,
                line_no,
                line,
                "UNSUPPORTED_GERBER_NEGATIVE_FILE_POLARITY",
                (
                    "negative Gerber file polarity represents absence of material "
                    "and image inversion is not modeled safely"
                ),
                out,
            )
            if not self.strict:
                self._disable_image_geometry(out)
            return

        out.diagnostics.append(
            ParseDiagnostic(
                "info",
                "GERBER_FILE_POLARITY_POSITIVE",
                "positive X2 .FilePolarity uses presence-of-material image semantics",
                str(path),
                line_no,
            )
        )

    def _handle_layer_polarity(
        self,
        line: str,
        path: Path,
        line_no: int,
        out: GerberLayerResult,
    ) -> None:
        match = _LAYER_POLARITY.match(line)
        if match is None:
            self._parse_error_or_warn(
                path,
                line_no,
                line,
                "INVALID_GERBER_LAYER_POLARITY",
                "invalid Gerber LP layer-polarity command",
                out,
            )
            if not self.strict:
                self._disable_image_geometry(out)
            return

        polarity = "clear" if match.group(1).upper() == "C" else "dark"
        self.layer_polarity = polarity
        if polarity == "clear":
            self._fail_or_warn(
                path,
                line_no,
                line,
                "UNSUPPORTED_GERBER_CLEAR_POLARITY",
                (
                    "clear Gerber layer polarity subtracts from previously created "
                    "objects; ordered clear/dark image composition is not modeled safely"
                ),
                out,
            )
            if not self.strict:
                self._disable_image_geometry(out)

    def _handle_aperture_transform(
        self,
        line: str,
        path: Path,
        line_no: int,
        out: GerberLayerResult,
    ) -> None:
        transform = None
        value = None

        match = _APERTURE_MIRROR.match(line)
        if match is not None:
            transform = "mirroring"
            value = match.group(1).upper()
            is_identity = value == "N"
        else:
            match = _APERTURE_ROTATION.match(line)
            if match is not None:
                transform = "rotation"
                value = float(match.group(1))
                normalized = value % 360.0
                is_identity = isclose(
                    normalized,
                    0.0,
                    rel_tol=0.0,
                    abs_tol=1e-12,
                ) or isclose(
                    normalized,
                    360.0,
                    rel_tol=0.0,
                    abs_tol=1e-12,
                )
            else:
                match = _APERTURE_SCALING.match(line)
                if match is not None:
                    transform = "scaling"
                    value = float(match.group(1))
                    if value <= 0:
                        self._parse_error_or_warn(
                            path,
                            line_no,
                            line,
                            "INVALID_GERBER_APERTURE_TRANSFORM",
                            "Gerber LS scaling factor must be greater than zero",
                            out,
                        )
                        if not self.strict:
                            self._disable_image_geometry(out)
                        return
                    is_identity = isclose(
                        value,
                        1.0,
                        rel_tol=0.0,
                        abs_tol=1e-12,
                    )
                else:
                    self._parse_error_or_warn(
                        path,
                        line_no,
                        line,
                        "INVALID_GERBER_APERTURE_TRANSFORM",
                        "invalid Gerber LM/LR/LS aperture-transform command",
                        out,
                    )
                    if not self.strict:
                        self._disable_image_geometry(out)
                    return

        if is_identity:
            return

        self._fail_or_warn(
            path,
            line_no,
            line,
            "UNSUPPORTED_GERBER_APERTURE_TRANSFORM",
            (
                f"non-identity Gerber aperture {transform} ({value}) changes "
                "object geometry and is not modeled safely"
            ),
            out,
        )
        if not self.strict:
            self._disable_image_geometry(out)

    def _decode(self, raw, axis):
        if raw is None:
            return None
        fmt = self.xfmt if axis == "x" else self.yfmt
        value = float(raw) if "." in raw else fmt.decode(raw)
        return to_mm(value, self.units)

    def _instantiate_standard_aperture(
        self,
        code: int,
        shape: str,
        modifier_text: str,
        path: Path,
        line_no: int,
        line: str,
        out: GerberLayerResult,
    ) -> None:
        try:
            values = [float(value) for value in modifier_text.split("X")]
        except ValueError:
            self._parse_error_or_warn(
                path,
                line_no,
                line,
                "INVALID_GERBER_STANDARD_APERTURE",
                "standard aperture modifiers must be numeric",
                out,
            )
            self.unsupported_apertures.add(code)
            return

        solid_parameter_count = 1 if shape == "C" else 2
        if len(values) == solid_parameter_count + 1:
            hole_diameter = values[-1]
            if hole_diameter <= 0:
                self._parse_error_or_warn(
                    path,
                    line_no,
                    line,
                    "INVALID_GERBER_APERTURE_HOLE",
                    "standard aperture hole diameter must be positive",
                    out,
                )
            else:
                self._fail_or_warn(
                    path,
                    line_no,
                    line,
                    "UNSUPPORTED_GERBER_APERTURE_HOLE",
                    (
                        f"{shape} standard aperture contains a {hole_diameter:.12g} "
                        "hole; holed aperture image subtraction is not modeled safely"
                    ),
                    out,
                )
            self.unsupported_apertures.add(code)
            return

        if len(values) != solid_parameter_count:
            self._parse_error_or_warn(
                path,
                line_no,
                line,
                "INVALID_GERBER_STANDARD_APERTURE",
                (
                    f"{shape} standard aperture requires "
                    f"{solid_parameter_count} solid modifier(s)"
                ),
                out,
            )
            self.unsupported_apertures.add(code)
            return

        ax = to_mm(values[0], self.units)
        ay = ax if shape == "C" else to_mm(values[1], self.units)
        self.apertures[code] = Aperture(code, shape, ax, ay)

    def _register_aperture_macro(
        self,
        line: str,
        path: Path,
        line_no: int,
        out: GerberLayerResult,
    ) -> None:
        inner = line[3:-1] if line.endswith("%") else line[3:]
        if "*" not in inner:
            self._fail_or_warn(
                path,
                line_no,
                line,
                "INVALID_GERBER_APERTURE_MACRO",
                "aperture macro has no body",
                out,
            )
            return
        name, body = inner.split("*", 1)
        name = name.strip()
        if not name:
            self._fail_or_warn(
                path,
                line_no,
                line,
                "INVALID_GERBER_APERTURE_MACRO",
                "aperture macro has no name",
                out,
            )
            return
        self.aperture_macros[name] = body

    def _instantiate_macro_aperture(
        self,
        code: int,
        name: str,
        modifier_text: str | None,
        path: Path,
        line_no: int,
        line: str,
        out: GerberLayerResult,
    ) -> None:
        body = self.aperture_macros.get(name)
        if body is None:
            self._fail_or_warn(
                path,
                line_no,
                line,
                "UNKNOWN_GERBER_APERTURE_MACRO",
                f"aperture macro {name!r} is not defined",
                out,
            )
            self.unsupported_apertures.add(code)
            return

        try:
            raw_modifiers = [] if not modifier_text else modifier_text.split("X")
            variables = {
                str(index + 1): float(value)
                for index, value in enumerate(raw_modifiers)
                if value != ""
            }
            primitives = parse_macro_body(body)
            evaluated = evaluate_macro(primitives, variables)
        except (ValueError, SyntaxError, ZeroDivisionError) as exc:
            self._fail_or_warn(
                path,
                line_no,
                line,
                "INVALID_GERBER_APERTURE_MACRO",
                f"aperture macro {name!r} could not be evaluated ({exc})",
                out,
            )
            self.unsupported_apertures.add(code)
            return

        if len(evaluated) != 1 or evaluated[0]["kind"] != "circle":
            self._fail_or_warn(
                path,
                line_no,
                line,
                "UNSUPPORTED_GERBER_APERTURE_MACRO",
                (
                    f"aperture macro {name!r} is not a single positive "
                    "centered circle"
                ),
                out,
            )
            self.unsupported_apertures.add(code)
            return

        values = evaluated[0]["values"]
        if len(values) < 4:
            self._fail_or_warn(
                path,
                line_no,
                line,
                "INVALID_GERBER_APERTURE_MACRO",
                f"circle aperture macro {name!r} has too few modifiers",
                out,
            )
            self.unsupported_apertures.add(code)
            return

        exposure, diameter, center_x, center_y = values[:4]
        rotation = values[4] if len(values) > 4 else 0.0
        if (
            exposure != 1
            or diameter <= 0
            or abs(center_x) > 1e-12
            or abs(center_y) > 1e-12
            or abs(rotation) > 1e-12
        ):
            self._fail_or_warn(
                path,
                line_no,
                line,
                "UNSUPPORTED_GERBER_APERTURE_MACRO",
                (
                    f"aperture macro {name!r} requires unsupported exposure, "
                    "offset, rotation, or diameter semantics"
                ),
                out,
            )
            self.unsupported_apertures.add(code)
            return

        diameter_mm = to_mm(float(diameter), self.units)
        self.apertures[code] = Aperture(code, "C", diameter_mm, diameter_mm)

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

    def _parse_error_or_warn(
        self,
        path: Path,
        line_no: int,
        raw: str,
        code: str,
        message: str,
        out: GerberLayerResult,
    ) -> None:
        if self.strict:
            raise ParseError(f"{path}:{line_no}: {message}: {raw}")
        out.diagnostics.append(
            ParseDiagnostic("warning", code, message, str(path), line_no)
        )

    def _arc_radius_tolerance_mm(self) -> float:
        x_resolution = to_mm(10 ** (-self.xfmt.decimal), self.units)
        y_resolution = to_mm(10 ** (-self.yfmt.decimal), self.units)
        return max(1e-6, 2.0 * max(x_resolution, y_resolution))

    def _resolve_arc_center(
        self,
        path: Path,
        line_no: int,
        line: str,
        out: GerberLayerResult,
        nxt: Point,
        i_raw: str | None,
        j_raw: str | None,
        clockwise: bool,
    ) -> Point | None:
        if self.quadrant_mode == "multi":
            if i_raw is None and j_raw is None:
                self._parse_error_or_warn(
                    path,
                    line_no,
                    line,
                    "GERBER_ARC_CENTER_MISSING",
                    "G75 arc draw requires I/J center offsets",
                    out,
                )
                return None
            i_mm = 0.0 if i_raw is None else self._decode(i_raw, "x")
            j_mm = 0.0 if j_raw is None else self._decode(j_raw, "y")
            return Point(self.current.x + i_mm, self.current.y + j_mm)

        if self.quadrant_mode != "single":
            self._fail_or_warn(
                path,
                line_no,
                line,
                "GERBER_ARC_QUADRANT_UNSUPPORTED",
                "arc draw requires explicit G74 or G75 quadrant mode",
                out,
            )
            return None

        if i_raw is None or j_raw is None:
            self._parse_error_or_warn(
                path,
                line_no,
                line,
                "GERBER_G74_CENTER_MISSING",
                "G74 single-quadrant arcs require both unsigned I and J distances",
                out,
            )
            return None

        i_mm = self._decode(i_raw, "x")
        j_mm = self._decode(j_raw, "y")
        if i_mm < 0 or j_mm < 0:
            self._parse_error_or_warn(
                path,
                line_no,
                line,
                "GERBER_G74_SIGNED_OFFSET",
                "G74 I/J values are unsigned center distances",
                out,
            )
            return None

        radius_tolerance = self._arc_radius_tolerance_mm()
        candidates: list[tuple[float, float, Point]] = []
        seen: set[tuple[float, float]] = set()

        for x_sign in (-1.0, 1.0):
            for y_sign in (-1.0, 1.0):
                center = Point(
                    self.current.x + x_sign * i_mm,
                    self.current.y + y_sign * j_mm,
                )
                key = (round(center.x, 15), round(center.y, 15))
                if key in seen:
                    continue
                seen.add(key)
                spec = ArcSpec(
                    GeoPoint(self.current.x, self.current.y),
                    GeoPoint(nxt.x, nxt.y),
                    GeoPoint(center.x, center.y),
                    clockwise=clockwise,
                )
                try:
                    start_radius, end_radius = arc_radii(spec)
                    validate_arc(
                        spec,
                        rel_tol=1e-6,
                        abs_tol=radius_tolerance,
                    )
                    sweep = abs(
                        sweep_radians(
                            spec,
                            rel_tol=1e-6,
                            abs_tol=radius_tolerance,
                        )
                    )
                except ValueError:
                    continue
                if sweep > (pi / 2) + 1e-9:
                    continue
                candidates.append(
                    (abs(start_radius - end_radius), sweep, center)
                )

        if not candidates:
            self._parse_error_or_warn(
                path,
                line_no,
                line,
                "GERBER_G74_CENTER_UNRESOLVED",
                (
                    "no G74 center candidate satisfies the requested direction, "
                    "radius tolerance, and <=90 degree sweep"
                ),
                out,
            )
            return None

        candidates.sort(
            key=lambda item: (item[0], item[1], item[2].x, item[2].y)
        )
        best_deviation = candidates[0][0]
        tie_tolerance = max(1e-12, radius_tolerance * 1e-6)
        best = [
            item
            for item in candidates
            if abs(item[0] - best_deviation) <= tie_tolerance
        ]
        if len(best) != 1:
            self._parse_error_or_warn(
                path,
                line_no,
                line,
                "GERBER_G74_CENTER_AMBIGUOUS",
                "multiple G74 center candidates have the same least deviation",
                out,
            )
            return None
        return best[0][2]

    def _emit_arc(
        self,
        path: Path,
        line_no: int,
        line: str,
        out: GerberLayerResult,
        nxt: Point,
        i_raw: str | None,
        j_raw: str | None,
        clockwise: bool,
    ) -> None:
        if self.quadrant_mode not in {"single", "multi"}:
            self._fail_or_warn(
                path,
                line_no,
                line,
                "GERBER_ARC_QUADRANT_UNSUPPORTED",
                "arc draw requires explicit G74 or G75 quadrant mode",
                out,
            )
            self.current = nxt
            return

        if (
            self.current_aperture is None
            or self.current_aperture not in self.apertures
        ):
            if (
                not self.strict
                and self.current_aperture in self.unsupported_apertures
            ):
                out.diagnostics.append(
                    ParseDiagnostic(
                        "warning",
                        "GERBER_APERTURE_GEOMETRY_SKIPPED",
                        (
                            "arc geometry skipped because the selected "
                            "aperture macro is unsupported"
                        ),
                        str(path),
                        line_no,
                    )
                )
                self.current = nxt
                return
            raise ParseError(
                f"{path}:{line_no}: arc draw before valid aperture selection"
            )

        aperture = self.apertures[self.current_aperture]
        if aperture.shape != "C":
            self._fail_or_warn(
                path,
                line_no,
                line,
                "GERBER_ARC_NON_CIRCULAR_APERTURE",
                "arc interpolation is supported only with circular draw apertures",
                out,
            )
            self.current = nxt
            return

        if self.quadrant_mode == "single" and self.current == nxt:
            if i_raw is None or j_raw is None:
                self._parse_error_or_warn(
                    path,
                    line_no,
                    line,
                    "GERBER_G74_CENTER_MISSING",
                    "G74 single-quadrant zero-length arc still requires I and J",
                    out,
                )
            else:
                i_mm = self._decode(i_raw, "x")
                j_mm = self._decode(j_raw, "y")
                if i_mm < 0 or j_mm < 0:
                    self._parse_error_or_warn(
                        path,
                        line_no,
                        line,
                        "GERBER_G74_SIGNED_OFFSET",
                        "G74 I/J values are unsigned center distances",
                        out,
                    )
            self.current = nxt
            return

        center = self._resolve_arc_center(
            path,
            line_no,
            line,
            out,
            nxt,
            i_raw,
            j_raw,
            clockwise,
        )
        if center is None:
            self.current = nxt
            return
        spec = ArcSpec(
            GeoPoint(self.current.x, self.current.y),
            GeoPoint(nxt.x, nxt.y),
            GeoPoint(center.x, center.y),
            clockwise=clockwise,
        )
        radius_tolerance = self._arc_radius_tolerance_mm()

        try:
            radius = validate_arc(
                spec,
                rel_tol=1e-6,
                abs_tol=radius_tolerance,
            )
            segment_count = segments_for_chord_error(
                spec,
                _ARC_MAX_CHORD_ERROR_MM,
                max_segments=_MAX_ARC_SEGMENTS,
                rel_tol=1e-6,
                abs_tol=radius_tolerance,
            )
            points = arc_points(
                spec,
                segments=segment_count,
                rel_tol=1e-6,
                abs_tol=radius_tolerance,
            )
        except ValueError as exc:
            self._parse_error_or_warn(
                path,
                line_no,
                line,
                "GERBER_ARC_INVALID",
                f"invalid {self.quadrant_mode.upper()} arc geometry ({exc})",
                out,
            )
            self.current = nxt
            return

        src = SourceRef(str(path), line_no, line)
        direction = "CW" if clockwise else "CCW"
        width = max(aperture.x, aperture.y)

        for x_index, y_index, dx_mm, dy_mm in self._iter_repetitions():
            repeated_center = Point(center.x + dx_mm, center.y + dy_mm)
            for segment_index in range(segment_count):
                start_geo = points[segment_index]
                end_geo = points[segment_index + 1]
                start = Point(start_geo.x + dx_mm, start_geo.y + dy_mm)
                end = Point(end_geo.x + dx_mm, end_geo.y + dy_mm)

                id_parts = [
                    path.name,
                    line_no,
                    self.current.x,
                    self.current.y,
                    nxt.x,
                    nxt.y,
                    center.x,
                    center.y,
                    direction,
                    segment_index,
                    segment_count,
                    width,
                    self.layer,
                ]
                if self.step_repeat is not None:
                    id_parts.extend(["sr", x_index, y_index])
                obj_id = stable_id("trk", *id_parts)

                prov = self._step_repeat_provenance(
                    src,
                    x_index or 0,
                    y_index or 0,
                    dx_mm,
                    dy_mm,
                )
                prov.add_evidence(
                    Evidence(
                        "gerber_arc_tessellation",
                        (
                            f"quadrant_mode={self.quadrant_mode}; "
                            f"direction={direction}; "
                            f"center_mm=({repeated_center.x:.12g},"
                            f"{repeated_center.y:.12g}); "
                            f"radius_mm={radius:.12g}; "
                            f"segment={segment_index + 1}/{segment_count}; "
                            f"max_chord_error_mm={_ARC_MAX_CHORD_ERROR_MM:.12g}"
                        ),
                        1.0,
                        src,
                    )
                )

                if self.layer == "Edge.Cuts":
                    out.outline.append(OutlineSegment(obj_id, start, end, prov))
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

        self.current = nxt

    def parse(self, path: str | Path) -> GerberLayerResult:
        p = Path(path)
        out = GerberLayerResult()

        text = p.read_text(encoding="utf-8-sig", errors="strict")
        for line_no, line in iter_gerber_statements(text):
            if not line or line.startswith("G04"):
                continue
            if line == "M02*":
                continue
            if line.startswith("%LP"):
                self._handle_layer_polarity(line, p, line_no, out)
                continue
            if line.startswith(("%LM", "%LR", "%LS")):
                self._handle_aperture_transform(line, p, line_no, out)
                continue
            if line.startswith("%TF.FilePolarity"):
                self._handle_file_polarity(line, p, line_no, out)
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

            # Legacy RS-274-D/early RS-274X unit commands still appear in
            # exported CAM jobs. Their semantics are unambiguous here.
            if line in {"G70*", "G070*"}:
                self.units = "inch"
                continue
            if line in {"G71*", "G071*"}:
                self.units = "mm"
                continue

            # PHOTONX models absolute coordinates. Explicit absolute mode is
            # therefore a safe no-op; incremental mode is rejected visibly.
            if line in {"G90*", "G090*"}:
                continue
            if line in {"G91*", "G091*"}:
                self._fail_or_warn(
                    p,
                    line_no,
                    line,
                    "GERBER_INCREMENTAL_COORDINATES_UNSUPPORTED",
                    "G91 incremental coordinate mode is not implemented",
                    out,
                )
                continue

            # Older generators may emit explicit default transform statements.
            # Only the identity forms are accepted; non-identity transforms
            # remain unsupported rather than being silently ignored.
            if line in {"%ASAXBY*%", "%IPPOS*%", "%MIA0B0*%", "%OFA0B0*%"}:
                continue
            if line.startswith(("%AS", "%IP", "%MI", "%OF")):
                self._fail_or_warn(
                    p,
                    line_no,
                    line,
                    "UNSUPPORTED_GERBER_TRANSFORM",
                    "non-default legacy Gerber transform is not implemented",
                    out,
                )
                continue

            if line.startswith("%AM"):
                self._register_aperture_macro(line, p, line_no, out)
                continue

            m = _AD_STANDARD.match(line)
            if m:
                code, shape, modifiers = m.groups()
                self._instantiate_standard_aperture(
                    int(code),
                    shape,
                    modifiers,
                    p,
                    line_no,
                    line,
                    out,
                )
                continue

            m = _AD_MACRO.match(line)
            if m:
                code, name, modifiers = m.groups()
                self._instantiate_macro_aperture(
                    int(code),
                    name,
                    modifiers,
                    p,
                    line_no,
                    line,
                    out,
                )
                continue

            m = _SELECT.match(line)
            if m and int(m.group(1)) >= 10:
                self.current_aperture = int(m.group(1))
                continue

            m = _OP_SELECT.match(line)
            if m:
                self.current_operation = m.group(1)
                continue

            if line.startswith("%SR"):
                self._configure_step_repeat(line, p, line_no, out)
                continue

            if line in {"G75*", "G075*"}:
                self.quadrant_mode = "multi"
                continue

            if line in {"G74*", "G074*"}:
                self.quadrant_mode = "single"
                continue

            if line in {"G01*", "G1*"}:
                self.interpolation = "linear"
                continue

            if line in {"G02*", "G2*"}:
                self.interpolation = "cw_arc"
                if self.quadrant_mode not in {"single", "multi"}:
                    self._fail_or_warn(
                        p,
                        line_no,
                        line,
                        "GERBER_ARC_QUADRANT_UNSUPPORTED",
                        "G02 arc mode requires explicit G74 or G75",
                        out,
                    )
                continue

            if line in {"G03*", "G3*"}:
                self.interpolation = "ccw_arc"
                if self.quadrant_mode not in {"single", "multi"}:
                    self._fail_or_warn(
                        p,
                        line_no,
                        line,
                        "GERBER_ARC_QUADRANT_UNSUPPORTED",
                        "G03 arc mode requires explicit G74 or G75",
                        out,
                    )
                continue

            arc_match = _ARC_COORD.match(line)
            if arc_match:
                gcode, x_raw, y_raw, i_raw, j_raw, op = arc_match.groups()
                operation = op or self.current_operation
                if op is not None:
                    self.current_operation = op
                arc_candidate = (
                    gcode is not None
                    or i_raw is not None
                    or j_raw is not None
                    or (
                        self.interpolation in {"cw_arc", "ccw_arc"}
                        and operation == "1"
                    )
                )
                if arc_candidate:
                    if gcode in {"G02", "G2"}:
                        self.interpolation = "cw_arc"
                    elif gcode in {"G03", "G3"}:
                        self.interpolation = "ccw_arc"

                    x = self._decode(x_raw, "x")
                    y = self._decode(y_raw, "y")
                    nxt = Point(
                        self.current.x if x is None else x,
                        self.current.y if y is None else y,
                    )

                    if not self.image_geometry_enabled:
                        self.current = nxt
                        continue

                    if operation == "2":
                        self.current = nxt
                        continue

                    if operation != "1":
                        self._parse_error_or_warn(
                            p,
                            line_no,
                            line,
                            "GERBER_ARC_DCODE_REQUIRED",
                            "arc interpolation requires explicit D01 or D02",
                            out,
                        )
                        self.current = nxt
                        continue

                    if self.interpolation not in {"cw_arc", "ccw_arc"}:
                        self._parse_error_or_warn(
                            p,
                            line_no,
                            line,
                            "GERBER_ARC_MODE_MISSING",
                            "I/J center offsets require active G02 or G03 interpolation",
                            out,
                        )
                        self.current = nxt
                        continue

                    self._emit_arc(
                        p,
                        line_no,
                        line,
                        out,
                        nxt,
                        i_raw,
                        j_raw,
                        clockwise=self.interpolation == "cw_arc",
                    )
                    continue

            if line.startswith(("G36", "G37")) or line.startswith("%AB"):
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
                operation = op or self.current_operation
                if op is not None:
                    self.current_operation = op
                x = self._decode(x_raw, "x")
                y = self._decode(y_raw, "y")
                nxt = Point(
                    self.current.x if x is None else x,
                    self.current.y if y is None else y,
                )

                if not self.image_geometry_enabled:
                    self.current = nxt
                    continue

                if operation is None:
                    self._parse_error_or_warn(
                        p,
                        line_no,
                        line,
                        "GERBER_OPERATION_MODE_MISSING",
                        "coordinate command has no D01/D02/D03 and no modal operation",
                        out,
                    )
                    self.current = nxt
                    continue

                if operation == "2":
                    self.current = nxt
                    continue

                if (
                    self.current_aperture is None
                    or self.current_aperture not in self.apertures
                ):
                    if (
                        not self.strict
                        and self.current_aperture in self.unsupported_apertures
                    ):
                        out.diagnostics.append(
                            ParseDiagnostic(
                                "warning",
                                "GERBER_APERTURE_GEOMETRY_SKIPPED",
                                (
                                    "geometry skipped because the selected "
                                    "aperture macro is unsupported"
                                ),
                                str(p),
                                line_no,
                            )
                        )
                        self.current = nxt
                        continue
                    raise ParseError(
                        f"{p}:{line_no}: draw/flash before valid aperture selection"
                    )

                ap = self.apertures[self.current_aperture]
                src = SourceRef(str(p), line_no, line)

                if operation == "1":
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

                elif operation == "3":
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
