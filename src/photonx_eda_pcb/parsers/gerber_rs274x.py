from __future__ import annotations

from dataclasses import dataclass, field
from math import atan2, cos, degrees, hypot, isclose, isfinite, pi, radians, sin
from pathlib import Path
import re

from shapely.geometry import LineString, MultiPoint, Polygon
from shapely.ops import unary_union

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
from ..geometry_kernel import region_shape
from ..gerber_image import (
    ImageCompositionStream,
    canonical_polygon_components,
    polygonize_aperture_track,
    polygonize_flash,
    polygonize_holed_flash,
    polygonize_regular_polygon_flash,
    polygonize_regular_polygon_track,
    polygonize_rotated_flash,
    polygonize_track,
    trace_polygon_operation_contributions,
)
from ..ids import stable_id
from ..models import CopperRegion, OutlineSegment, PadCandidate, ParseDiagnostic, Point, Track
from ..provenance import Evidence, Provenance, SourceRef
from ..units import CoordinateFormat, to_mm
from .gerber_parts.region_state import RegionState
from .gerber_parts.step_repeat import parse_step_repeat
from .gerber_parts.tokenizer import iter_gerber_statements


_FS = re.compile(r"^%FS([LT])([AI])?X([0-9])([0-9])Y([0-9])([0-9])\*%$")
_MO = re.compile(r"^%MO(MM|IN)\*%$")
_AD_STANDARD = re.compile(
    r"^%ADD([0-9]+)([CROP]),?"
    r"([+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)"
    r"(?:X[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+))*)\*%$"
)
_AD_MACRO = re.compile(r"^%ADD([0-9]+)([A-Za-z_.$][A-Za-z0-9_.$-]*)(?:,([^*]*))?\*%$")
_SELECT = re.compile(r"^(?:G54)?D([0-9]+)\*$")
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
_IMAGE_ROTATION = re.compile(r"^%IR(0|90|180|270)\*%$", re.IGNORECASE)
_MIRROR_IMAGE = re.compile(
    r"^%MI(?:A([01]))?(?:B([01]))?\*%$",
    re.IGNORECASE,
)
_AXIS_SELECT = re.compile(r"^%AS(AXBY|AYBX)\*%$", re.IGNORECASE)
_IMAGE_NAME = re.compile(r"^%IN([^*%]+)\*%$")
_LOAD_NAME = re.compile(r"^%LN([^*%]+)\*%$")
_LEGACY_OFFSET = re.compile(
    r"^%OF"
    r"(?:A([+-]?(?:[0-9]+(?:\.[0-9]{1,5})?|\.[0-9]{1,5})))?"
    r"(?:B([+-]?(?:[0-9]+(?:\.[0-9]{1,5})?|\.[0-9]{1,5})))?"
    r"\*%$",
    re.IGNORECASE,
)
_LEGACY_SCALE_FACTOR = re.compile(
    r"^%SF"
    r"(?:A([0-9]+(?:\.[0-9]*)?|\.[0-9]+))?"
    r"(?:B([0-9]+(?:\.[0-9]*)?|\.[0-9]+))?"
    r"\*%$",
    re.IGNORECASE,
)

_MAX_STEP_REPEAT_INSTANCES = 10_000
_ARC_MAX_CHORD_ERROR_MM = 0.005
_MAX_ARC_SEGMENTS = 4096

_ASCII_DECIMAL_DIGITS = frozenset("0123456789")


def _contains_non_ascii_decimal_digit(text: str) -> bool:
    """Return whether text contains a Unicode decimal digit outside ASCII."""

    return any(
        character.isdecimal() and character not in _ASCII_DECIMAL_DIGITS
        for character in text
    )


def _is_structured_numeric_statement(line: str) -> bool:
    """Return whether line carries a numeric token parsed by this module."""

    return (
        line.startswith("%FS")
        or line.startswith("%ADD")
        or line.startswith("D")
        or line.startswith("G54D")
    )



@dataclass(frozen=True)
class Aperture:
    code: int
    shape: str
    x: float
    y: float
    hole_diameter: float | None = None
    base_rotation_deg: float = 0.0
    polygon_vertices: int | None = None
    polygon_rotation_deg: float = 0.0
    outline_vertices: tuple[tuple[float, float], ...] | None = None
    outline_rotation_deg: float = 0.0


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
    regions: list[CopperRegion] = field(default_factory=list)
    outline: list[OutlineSegment] = field(default_factory=list)
    diagnostics: list[ParseDiagnostic] = field(default_factory=list)


class GerberRS274XParser:
    """Strict, auditable RS-274X subset parser.

    Supported: FS, MO, ADD(C/R/O/P), Dnn selection, G01/D01/D02/D03,
    linear C/R/O/P aperture draws plus standard P and valid general Code-4
    outline-macro D03 flashes on material layers,
    bounded G74 single-quadrant
    and G75 multi-quadrant G02/G03 circular
    interpolation with circular apertures, dark multi-contour linear/G74/G75
    G36/G37 regions with bounded multi-hole cut-ins, G04, M02, and standard
    linear step-and-repeat
    (%SR...*% / %SR*%).

    Unsupported constructs are never silently discarded in strict mode.
    """

    def __init__(self, layer: str, strict: bool = True):
        self.layer = layer
        self.strict = strict
        self.units = "mm"
        self.units_declared = False
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
        self.region_state = RegionState()
        self.region_sources: list[SourceRef] = []
        self.region_arc_evidence: list[Evidence] = []
        self.region_contours: list[tuple[Point, ...]] = []
        self.region_contour_holes: list[tuple[tuple[Point, ...], ...]] = []
        self.region_contour_sources: list[list[SourceRef]] = []
        self.region_contour_arc_evidence: list[list[Evidence]] = []
        self.region_contour_cutin_evidence: list[list[Evidence]] = []
        self.region_current_sources: list[SourceRef] = []
        self.region_current_arc_evidence: list[Evidence] = []
        self.region_current_edge_kinds: list[str] = []
        self.region_start_line: int | None = None
        self.file_polarity: str | None = None
        self.layer_polarity = "dark"
        self.layer_polarity_sources: list[SourceRef] = []
        self.first_clear_polarity_source: SourceRef | None = None
        self.clear_polarity_seen = False
        self.material_image_operations = ImageCompositionStream[object]()
        self.image_geometry_enabled = True
        self.incremental = False
        self.image_rotation_deg = 0
        self.image_rotation_source: SourceRef | None = None
        self.mirror_a = False
        self.mirror_b = False
        self.mirror_image_source: SourceRef | None = None
        self.offset_a_mm = 0.0
        self.offset_b_mm = 0.0
        self.offset_source: SourceRef | None = None
        self.scale_a = 1.0
        self.scale_b = 1.0
        self.scale_source: SourceRef | None = None
        self.axis_select_source: SourceRef | None = None
        self.image_name_source: SourceRef | None = None
        self.image_polarity_source: SourceRef | None = None
        self.aperture_mirror = "N"
        self.aperture_rotation_deg = 0.0
        self.aperture_scale = 1.0
        self.aperture_mirror_source: SourceRef | None = None
        self.aperture_rotation_source: SourceRef | None = None
        self.aperture_scale_source: SourceRef | None = None
        self.image_body_started = False

    def _fail_or_warn(self, path, line_no, raw, code, message, out):
        if self.strict:
            raise UnsupportedFeatureError(f"{path}:{line_no}: {message}: {raw}")
        out.diagnostics.append(
            ParseDiagnostic("warning", code, message, str(path), line_no)
        )

    def _record_zero_size_object(
        self,
        path: Path,
        line_no: int,
        raw: str,
        out: GerberLayerResult,
        operation: str,
    ) -> None:
        """Record a legal C0 object that has no image effect."""

        out.diagnostics.append(
            ParseDiagnostic(
                "info",
                "GERBER_ZERO_SIZE_OBJECT_NO_IMAGE",
                (
                    "zero-diameter C aperture object has no image effect "
                    f"(operation=D0{operation})"
                ),
                str(path),
                line_no,
            )
        )

    def _disable_image_geometry(self, out: GerberLayerResult) -> None:
        """Prevent unsupported file-image semantics from leaking geometry."""
        self.image_geometry_enabled = False
        out.tracks.clear()
        out.pads.clear()
        out.regions.clear()
        out.outline.clear()
        self.material_image_operations.clear()

    def _declare_units(
        self,
        units: str,
        path: Path,
        line_no: int,
        raw: str,
        out: GerberLayerResult,
    ) -> bool:
        if self.units_declared:
            if self.units != units:
                self._fail_or_warn(
                    path,
                    line_no,
                    raw,
                    "CONFLICTING_GERBER_UNITS",
                    (
                        "Gerber unit mode changed after it was already declared "
                        f"({self.units} -> {units})"
                    ),
                    out,
                )
                if not self.strict:
                    self._disable_image_geometry(out)
                return False
            return True

        self.units = units
        self.units_declared = True
        return True

    def _require_units(
        self,
        path: Path,
        line_no: int,
        raw: str,
        out: GerberLayerResult,
    ) -> bool:
        if self.units_declared:
            return True
        self._parse_error_or_warn(
            path,
            line_no,
            raw,
            "GERBER_UNITS_UNDECLARED",
            (
                "Gerber dimensional data encountered before explicit "
                "MO/G70/G71 unit declaration"
            ),
            out,
        )
        if not self.strict:
            self._disable_image_geometry(out)
        return False

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
        source = SourceRef(str(path), line_no, line)
        self.layer_polarity_sources.append(source)
        if polarity == "clear":
            self.clear_polarity_seen = True
            if self.first_clear_polarity_source is None:
                self.first_clear_polarity_source = source
            out.diagnostics.append(
                ParseDiagnostic(
                    "info",
                    "GERBER_CLEAR_POLARITY_REGION_COMPOSITION",
                    (
                        "clear layer polarity is enabled for ordered polygon "
                        "composition of supported G36/G37 regions, C/R/O/P D03 "
                        "flashes, valid Code-4 outline-macro D03 flashes, linear "
                        "C/R/O/P D01 aperture sweeps, and bounded "
                        "circular-aperture G02/G03 tessellation; curved boundaries use evidenced chord-"
                        "error bounds while outlines remain fail-closed"
                    ),
                    str(path),
                    line_no,
                )
            )

    def _handle_aperture_transform(
        self,
        line: str,
        path: Path,
        line_no: int,
        out: GerberLayerResult,
    ) -> None:
        match = _APERTURE_MIRROR.match(line)
        if match is not None:
            self.aperture_mirror = match.group(1).upper()
            self.aperture_mirror_source = SourceRef(str(path), line_no, line)
            return

        match = _APERTURE_ROTATION.match(line)
        if match is not None:
            value = float(match.group(1))
            if not isfinite(value):
                self._parse_error_or_warn(
                    path,
                    line_no,
                    line,
                    "INVALID_GERBER_APERTURE_TRANSFORM",
                    "Gerber LR rotation must be finite",
                    out,
                )
                if not self.strict:
                    self._disable_image_geometry(out)
                return
            self.aperture_rotation_deg = value % 360.0
            self.aperture_rotation_source = SourceRef(str(path), line_no, line)
            return

        match = _APERTURE_SCALING.match(line)
        if match is not None:
            value = float(match.group(1))
            if not isfinite(value) or value <= 0:
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
            self.aperture_scale = value
            self.aperture_scale_source = SourceRef(str(path), line_no, line)
            return

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

    def _aperture_transform_id_parts(self) -> list[object]:
        parts: list[object] = []
        if self.aperture_mirror != "N":
            parts.extend(["lm", self.aperture_mirror])
        if not isclose(
            self.aperture_rotation_deg, 0.0, rel_tol=0.0, abs_tol=1e-12
        ):
            parts.extend(["lr", self.aperture_rotation_deg])
        if not isclose(
            self.aperture_scale, 1.0, rel_tol=0.0, abs_tol=1e-12
        ):
            parts.extend(["ls", self.aperture_scale])
        return parts

    def _add_aperture_transform_provenance(self, prov: Provenance) -> None:
        if self.aperture_mirror != "N" and self.aperture_mirror_source is not None:
            prov.add_source(self.aperture_mirror_source)
            prov.add_evidence(
                Evidence(
                    "gerber_aperture_mirror",
                    f"mirror={self.aperture_mirror}",
                    1.0,
                    self.aperture_mirror_source,
                )
            )
        if (
            not isclose(
                self.aperture_rotation_deg, 0.0, rel_tol=0.0, abs_tol=1e-12
            )
            and self.aperture_rotation_source is not None
        ):
            prov.add_source(self.aperture_rotation_source)
            prov.add_evidence(
                Evidence(
                    "gerber_aperture_rotation",
                    f"rotation_deg_ccw={self.aperture_rotation_deg:.12g}",
                    1.0,
                    self.aperture_rotation_source,
                )
            )
        if (
            not isclose(self.aperture_scale, 1.0, rel_tol=0.0, abs_tol=1e-12)
            and self.aperture_scale_source is not None
        ):
            prov.add_source(self.aperture_scale_source)
            prov.add_evidence(
                Evidence(
                    "gerber_aperture_scale",
                    f"scale={self.aperture_scale:.12g}",
                    1.0,
                    self.aperture_scale_source,
                )
            )

    def _transformed_aperture_size(
        self,
        aperture: Aperture,
        path: Path,
        line_no: int,
        line: str,
        out: GerberLayerResult,
    ) -> tuple[float, float] | None:
        size_x = aperture.x * self.aperture_scale
        size_y = aperture.y * self.aperture_scale

        # Circles are rotation-invariant. Rectangular/obround apertures may
        # carry intrinsic rotation from an exactly reduced aperture macro; LM
        # reflects that original orientation before modal LR.
        if aperture.shape == "C":
            return size_x, size_y

        rotated = self._orthogonal_rectangle_size(
            size_x,
            size_y,
            self._effective_rectangular_aperture_rotation(
                aperture,
                include_image_rotation=False,
            ),
        )
        if rotated is not None:
            return rotated

        self._fail_or_warn(
            path,
            line_no,
            line,
            "UNSUPPORTED_GERBER_APERTURE_TRANSFORM",
            (
                f"Gerber LR{self.aperture_rotation_deg:.12g} rotates "
                f"{aperture.shape} aperture D{aperture.code} to a non-axis-aligned "
                "shape for a flash outside the current PadCandidate representation"
            ),
            out,
        )
        if not self.strict:
            self._disable_image_geometry(out)
        return None

    def _handle_axis_select(
        self,
        line: str,
        path: Path,
        line_no: int,
        out: GerberLayerResult,
    ) -> None:
        match = _AXIS_SELECT.match(line)
        if match is None:
            self._parse_error_or_warn(
                path,
                line_no,
                line,
                "INVALID_GERBER_AXIS_SELECT",
                "legacy Gerber AS must be AXBY or AYBX",
                out,
            )
            if not self.strict:
                self._disable_image_geometry(out)
            return

        if self.axis_select_source is not None:
            self._parse_error_or_warn(
                path,
                line_no,
                line,
                "DUPLICATE_GERBER_AXIS_SELECT",
                "legacy Gerber AS may only be declared once",
                out,
            )
            if not self.strict:
                self._disable_image_geometry(out)
            return

        if self.image_body_started:
            self._parse_error_or_warn(
                path,
                line_no,
                line,
                "LATE_GERBER_AXIS_SELECT",
                "legacy Gerber AS must appear before any coordinate data",
                out,
            )
            if not self.strict:
                self._disable_image_geometry(out)
            return

        self.axis_select_source = SourceRef(str(path), line_no, line)
        out.diagnostics.append(
            ParseDiagnostic(
                "info",
                "GERBER_AXIS_SELECT_OUTPUT_DEVICE_ONLY",
                (
                    f"legacy AS {match.group(1).upper()} affects only output-device "
                    "axis assignment and does not alter CAD-to-CAM image geometry"
                ),
                str(path),
                line_no,
            )
        )

    def _handle_image_polarity(
        self,
        line: str,
        path: Path,
        line_no: int,
        out: GerberLayerResult,
    ) -> None:
        """Handle the deprecated whole-image IP command conservatively.

        Positive image polarity is the normal Gerber image semantics already used
        by the parser. Negative image polarity inverts the infinite image plane
        and therefore remains fail-closed until an explicit bounded image-plane
        representation exists.
        """

        if line != "%IPPOS*%":
            self._fail_or_warn(
                path,
                line_no,
                line,
                "UNSUPPORTED_GERBER_TRANSFORM",
                (
                    "negative or malformed legacy Gerber IP image polarity changes "
                    "image geometry and whole-image semantics and is not implemented safely"
                ),
                out,
            )
            if not self.strict:
                self._disable_image_geometry(out)
            return

        if self.image_polarity_source is not None:
            self._parse_error_or_warn(
                path,
                line_no,
                line,
                "DUPLICATE_GERBER_IMAGE_POLARITY",
                "legacy Gerber IP may only be declared once",
                out,
            )
            if not self.strict:
                self._disable_image_geometry(out)
            return

        if self.image_body_started:
            self._parse_error_or_warn(
                path,
                line_no,
                line,
                "LATE_GERBER_IMAGE_POLARITY",
                "legacy Gerber IP must appear before any coordinate data",
                out,
            )
            if not self.strict:
                self._disable_image_geometry(out)
            return

        self.image_polarity_source = SourceRef(str(path), line_no, line)
        out.diagnostics.append(
            ParseDiagnostic(
                "info",
                "GERBER_IMAGE_POLARITY_POSITIVE",
                "legacy IPPOS selects the default positive whole-image polarity",
                str(path),
                line_no,
            )
        )

    def _handle_image_name(
        self,
        line: str,
        path: Path,
        line_no: int,
        out: GerberLayerResult,
    ) -> None:
        match = _IMAGE_NAME.match(line)
        if match is None:
            self._parse_error_or_warn(
                path,
                line_no,
                line,
                "INVALID_GERBER_IMAGE_NAME",
                "invalid legacy Gerber IN image-name command",
                out,
            )
            return
        if self.image_name_source is not None:
            self._parse_error_or_warn(
                path,
                line_no,
                line,
                "DUPLICATE_GERBER_IMAGE_NAME",
                "legacy Gerber IN may only be declared once",
                out,
            )
            return
        if self.image_body_started:
            self._parse_error_or_warn(
                path,
                line_no,
                line,
                "LATE_GERBER_IMAGE_NAME",
                "legacy Gerber IN must appear before any coordinate data",
                out,
            )
            return
        self.image_name_source = SourceRef(str(path), line_no, line)
        out.diagnostics.append(
            ParseDiagnostic(
                "info",
                "GERBER_IMAGE_NAME_COMMENT",
                f"legacy IN image name: {match.group(1)}",
                str(path),
                line_no,
            )
        )

    def _handle_load_name(
        self,
        line: str,
        path: Path,
        line_no: int,
        out: GerberLayerResult,
    ) -> None:
        match = _LOAD_NAME.match(line)
        if match is None:
            self._parse_error_or_warn(
                path,
                line_no,
                line,
                "INVALID_GERBER_LOAD_NAME",
                "invalid legacy Gerber LN load-name command",
                out,
            )
            return
        out.diagnostics.append(
            ParseDiagnostic(
                "info",
                "GERBER_LOAD_NAME_COMMENT",
                f"legacy LN section name: {match.group(1)}",
                str(path),
                line_no,
            )
        )

    def _handle_mirror_image(
        self,
        line: str,
        path: Path,
        line_no: int,
        out: GerberLayerResult,
    ) -> None:
        match = _MIRROR_IMAGE.match(line)
        if match is None:
            self._fail_or_warn(
                path,
                line_no,
                line,
                "INVALID_GERBER_MIRROR_IMAGE",
                "legacy Gerber MI accepts only optional A0/A1 and B0/B1 factors",
                out,
            )
            if not self.strict:
                self._disable_image_geometry(out)
            return

        if self.mirror_image_source is not None:
            self._fail_or_warn(
                path,
                line_no,
                line,
                "DUPLICATE_GERBER_MIRROR_IMAGE",
                "legacy Gerber MI may only be declared once",
                out,
            )
            if not self.strict:
                self._disable_image_geometry(out)
            return

        if self.image_body_started:
            self._fail_or_warn(
                path,
                line_no,
                line,
                "LATE_GERBER_MIRROR_IMAGE",
                "legacy Gerber MI must precede any coordinate data",
                out,
            )
            if not self.strict:
                self._disable_image_geometry(out)
            return

        self.mirror_a = match.group(1) == "1"
        self.mirror_b = match.group(2) == "1"
        self.mirror_image_source = SourceRef(str(path), line_no, line)

    def _handle_legacy_offset(
        self,
        line: str,
        path: Path,
        line_no: int,
        out: GerberLayerResult,
    ) -> None:
        match = _LEGACY_OFFSET.match(line)
        if match is None:
            self._fail_or_warn(
                path,
                line_no,
                line,
                "INVALID_GERBER_OFFSET",
                "invalid legacy Gerber OF offset command",
                out,
            )
            if not self.strict:
                self._disable_image_geometry(out)
            return

        if not self._require_units(path, line_no, line, out):
            return

        if self.offset_source is not None:
            self._fail_or_warn(
                path,
                line_no,
                line,
                "DUPLICATE_GERBER_OFFSET",
                "legacy Gerber OF may only be declared once",
                out,
            )
            if not self.strict:
                self._disable_image_geometry(out)
            return

        if self.image_body_started:
            self._fail_or_warn(
                path,
                line_no,
                line,
                "LATE_GERBER_OFFSET",
                "legacy Gerber OF must precede any coordinate data",
                out,
            )
            if not self.strict:
                self._disable_image_geometry(out)
            return

        a_value = 0.0 if match.group(1) is None else float(match.group(1))
        b_value = 0.0 if match.group(2) is None else float(match.group(2))
        if abs(a_value) > 99999.99999 or abs(b_value) > 99999.99999:
            self._fail_or_warn(
                path,
                line_no,
                line,
                "INVALID_GERBER_OFFSET",
                "legacy Gerber OF offsets must be within +/-99999.99999 units",
                out,
            )
            if not self.strict:
                self._disable_image_geometry(out)
            return

        self.offset_a_mm = to_mm(a_value, self.units)
        self.offset_b_mm = to_mm(b_value, self.units)
        self.offset_source = SourceRef(str(path), line_no, line)

    def _handle_image_rotation(
        self,
        line: str,
        path: Path,
        line_no: int,
        out: GerberLayerResult,
    ) -> None:
        match = _IMAGE_ROTATION.match(line)
        if match is None:
            self._fail_or_warn(
                path,
                line_no,
                line,
                "INVALID_GERBER_IMAGE_ROTATION",
                "legacy Gerber IR rotation must be one of 0, 90, 180, or 270 degrees",
                out,
            )
            if not self.strict:
                self._disable_image_geometry(out)
            return

        if self.image_rotation_source is not None:
            self._fail_or_warn(
                path,
                line_no,
                line,
                "DUPLICATE_GERBER_IMAGE_ROTATION",
                "legacy Gerber IR may only be declared once",
                out,
            )
            if not self.strict:
                self._disable_image_geometry(out)
            return

        if self.image_body_started:
            self._fail_or_warn(
                path,
                line_no,
                line,
                "LATE_GERBER_IMAGE_ROTATION",
                "legacy Gerber IR must precede any coordinate data",
                out,
            )
            if not self.strict:
                self._disable_image_geometry(out)
            return

        self.image_rotation_deg = int(match.group(1))
        self.image_rotation_source = SourceRef(str(path), line_no, line)

    def _handle_legacy_scale_factor(
        self,
        line: str,
        path: Path,
        line_no: int,
        out: GerberLayerResult,
    ) -> None:
        match = _LEGACY_SCALE_FACTOR.match(line)
        if match is None:
            self._fail_or_warn(
                path,
                line_no,
                line,
                "INVALID_GERBER_SCALE_FACTOR",
                "invalid legacy Gerber SF scale-factor command",
                out,
            )
            if not self.strict:
                self._disable_image_geometry(out)
            return

        if self.scale_source is not None:
            self._fail_or_warn(
                path,
                line_no,
                line,
                "DUPLICATE_GERBER_SCALE_FACTOR",
                "legacy Gerber SF may only be declared once",
                out,
            )
            if not self.strict:
                self._disable_image_geometry(out)
            return

        if self.image_body_started:
            self._fail_or_warn(
                path,
                line_no,
                line,
                "LATE_GERBER_SCALE_FACTOR",
                "legacy Gerber SF must precede any coordinate data",
                out,
            )
            if not self.strict:
                self._disable_image_geometry(out)
            return

        a_scale = 1.0 if match.group(1) is None else float(match.group(1))
        b_scale = 1.0 if match.group(2) is None else float(match.group(2))
        if not (0.0001 <= a_scale <= 999.99999) or not (
            0.0001 <= b_scale <= 999.99999
        ):
            self._fail_or_warn(
                path,
                line_no,
                line,
                "INVALID_GERBER_SCALE_FACTOR",
                "legacy Gerber SF factors must be between 0.0001 and 999.99999",
                out,
            )
            if not self.strict:
                self._disable_image_geometry(out)
            return

        self.scale_a = a_scale
        self.scale_b = b_scale
        self.scale_source = SourceRef(str(path), line_no, line)

    def _mirror_coordinate_point(self, point: Point) -> Point:
        return Point(
            -point.x if self.mirror_a else point.x,
            -point.y if self.mirror_b else point.y,
        )

    def _output_arc_direction(self, clockwise: bool) -> str:
        # A reflection over exactly one axis reverses planar orientation.
        # Positive SF, translation, and rotation preserve orientation.
        reflected_once = self.mirror_a ^ self.mirror_b
        output_clockwise = bool(clockwise) ^ reflected_once
        return "CW" if output_clockwise else "CCW"

    def _rotate_image_point(self, point: Point) -> Point:
        if self.image_rotation_deg == 90:
            return Point(-point.y, point.x)
        if self.image_rotation_deg == 180:
            return Point(-point.x, -point.y)
        if self.image_rotation_deg == 270:
            return Point(point.y, -point.x)
        return point

    def _rotate_image_size(self, x: float, y: float) -> tuple[float, float]:
        if self.image_rotation_deg in {90, 270}:
            return y, x
        return x, y

    def _transform_output_point(
        self,
        point: Point,
        dx_mm: float = 0.0,
        dy_mm: float = 0.0,
    ) -> Point:
        mirrored = self._mirror_coordinate_point(point)
        scaled = Point(
            mirrored.x * self.scale_a,
            mirrored.y * self.scale_b,
        )
        # MI/SF affect coordinate data only. Step-repeat distances are not
        # coordinate data, so they are added afterwards and are neither mirrored
        # nor scaled. OF then translates the whole image before IR.
        repeated = Point(scaled.x + dx_mm, scaled.y + dy_mm)
        offset = Point(
            repeated.x + self.offset_a_mm,
            repeated.y + self.offset_b_mm,
        )
        return self._rotate_image_point(offset)

    def _image_transform_id_parts(self) -> list[object]:
        parts: list[object] = []
        if self.mirror_a or self.mirror_b:
            parts.extend(["mi", int(self.mirror_a), int(self.mirror_b)])
        if not isclose(self.scale_a, 1.0, rel_tol=0.0, abs_tol=1e-12) or not isclose(
            self.scale_b, 1.0, rel_tol=0.0, abs_tol=1e-12
        ):
            parts.extend(["sf", self.scale_a, self.scale_b])
        if self.offset_a_mm or self.offset_b_mm:
            parts.extend(["of", self.offset_a_mm, self.offset_b_mm])
        if self.image_rotation_deg:
            parts.extend(["ir", self.image_rotation_deg])
        return parts

    def _decode(self, raw, axis):
        if raw is None:
            return None
        fmt = self.xfmt if axis == "x" else self.yfmt
        value = float(raw) if "." in raw else fmt.decode(raw)
        return to_mm(value, self.units)

    def _coordinate_point(self, x_raw, y_raw) -> Point:
        x = self._decode(x_raw, "x")
        y = self._decode(y_raw, "y")
        if self.incremental:
            return Point(
                self.current.x + (0.0 if x is None else x),
                self.current.y + (0.0 if y is None else y),
            )
        return Point(
            self.current.x if x is None else x,
            self.current.y if y is None else y,
        )

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

        if shape == "P":
            if len(values) not in {2, 3, 4}:
                self._parse_error_or_warn(
                    path,
                    line_no,
                    line,
                    "INVALID_GERBER_STANDARD_POLYGON_APERTURE",
                    (
                        "P standard aperture requires outer diameter and vertex "
                        "count, with optional rotation and round-hole diameter"
                    ),
                    out,
                )
                self.unsupported_apertures.add(code)
                return

            outer_diameter = values[0]
            vertices_value = values[1]
            rotation = values[2] if len(values) >= 3 else 0.0
            hole_diameter = values[3] if len(values) == 4 else None

            if outer_diameter <= 0:
                self._parse_error_or_warn(
                    path,
                    line_no,
                    line,
                    "INVALID_GERBER_STANDARD_APERTURE_SIZE",
                    "P standard aperture outer diameter must be positive",
                    out,
                )
                self.unsupported_apertures.add(code)
                return
            if (
                not isfinite(vertices_value)
                or not vertices_value.is_integer()
                or not 3 <= int(vertices_value) <= 12
            ):
                self._parse_error_or_warn(
                    path,
                    line_no,
                    line,
                    "INVALID_GERBER_POLYGON_VERTEX_COUNT",
                    "P standard aperture vertex count must be an integer in 3..12",
                    out,
                )
                self.unsupported_apertures.add(code)
                return
            if not isfinite(rotation):
                self._parse_error_or_warn(
                    path,
                    line_no,
                    line,
                    "INVALID_GERBER_POLYGON_ROTATION",
                    "P standard aperture rotation must be finite",
                    out,
                )
                self.unsupported_apertures.add(code)
                return

            vertices = int(vertices_value)
            if hole_diameter is not None:
                if hole_diameter <= 0:
                    self._parse_error_or_warn(
                        path,
                        line_no,
                        line,
                        "INVALID_GERBER_APERTURE_HOLE",
                        "standard aperture hole diameter must be positive",
                        out,
                    )
                    self.unsupported_apertures.add(code)
                    return
                max_hole = outer_diameter * cos(pi / vertices)
                if hole_diameter >= max_hole:
                    self._parse_error_or_warn(
                        path,
                        line_no,
                        line,
                        "INVALID_GERBER_APERTURE_HOLE_FIT",
                        (
                            "P standard aperture round hole must strictly fit "
                            "inside the regular polygon"
                        ),
                        out,
                    )
                    self.unsupported_apertures.add(code)
                    return

            outer_mm = to_mm(outer_diameter, self.units)
            hole_mm = (
                None
                if hole_diameter is None
                else to_mm(hole_diameter, self.units)
            )
            self.apertures[code] = Aperture(
                code,
                "P",
                outer_mm,
                outer_mm,
                hole_mm,
                polygon_vertices=vertices,
                polygon_rotation_deg=rotation % 360.0,
            )
            return

        solid_parameter_count = 1 if shape == "C" else 2
        if len(values) not in {solid_parameter_count, solid_parameter_count + 1}:
            self._parse_error_or_warn(
                path,
                line_no,
                line,
                "INVALID_GERBER_STANDARD_APERTURE",
                (
                    f"{shape} standard aperture requires "
                    f"{solid_parameter_count} solid modifier(s)"
                    " with at most one trailing round-hole modifier"
                ),
                out,
            )
            self.unsupported_apertures.add(code)
            return

        if shape == "C" and values[0] < 0:
            self._parse_error_or_warn(
                path,
                line_no,
                line,
                "INVALID_GERBER_STANDARD_APERTURE_SIZE",
                "C standard aperture diameter must be non-negative",
                out,
            )
            self.unsupported_apertures.add(code)
            return

        if shape in {"R", "O"} and (values[0] <= 0 or values[1] <= 0):
            self._parse_error_or_warn(
                path,
                line_no,
                line,
                "INVALID_GERBER_STANDARD_APERTURE_SIZE",
                f"{shape} standard aperture X/Y sizes must both be positive",
                out,
            )
            self.unsupported_apertures.add(code)
            return

        hole_diameter = None
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
                self.unsupported_apertures.add(code)
                return
            outer_limit = min(values[:solid_parameter_count])
            if hole_diameter >= outer_limit:
                self._parse_error_or_warn(
                    path,
                    line_no,
                    line,
                    "INVALID_GERBER_APERTURE_HOLE_FIT",
                    (
                        "standard aperture round hole must strictly fit within "
                        f"the {shape} outer shape"
                    ),
                    out,
                )
                self.unsupported_apertures.add(code)
                return

        ax = to_mm(values[0], self.units)
        ay = ax if shape == "C" else to_mm(values[1], self.units)
        hole_mm = (
            None
            if hole_diameter is None
            else to_mm(hole_diameter, self.units)
        )
        self.apertures[code] = Aperture(code, shape, ax, ay, hole_mm)

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

    @staticmethod
    def _orthogonal_rectangle_size(
        width: float,
        height: float,
        rotation: float,
    ) -> tuple[float, float] | None:
        """Return exact axis-aligned dimensions for a 90-degree-step rotation."""
        normalized = rotation % 360.0
        angle = None
        for candidate in (0.0, 90.0, 180.0, 270.0):
            if isclose(normalized, candidate, rel_tol=0.0, abs_tol=1e-9):
                angle = candidate
                break
        if angle is None:
            return None
        if angle in {90.0, 270.0}:
            return height, width
        return width, height

    def _effective_rectangular_aperture_rotation(
        self,
        aperture: Aperture,
        *,
        include_image_rotation: bool = True,
    ) -> float:
        """Compose intrinsic macro rotation, LM reflection, LR, and optional IR."""

        angle = radians(aperture.base_rotation_deg)
        dx = cos(angle)
        dy = sin(angle)
        if "X" in self.aperture_mirror:
            dx = -dx
        if "Y" in self.aperture_mirror:
            dy = -dy
        rotation = degrees(atan2(dy, dx)) + self.aperture_rotation_deg
        if include_image_rotation:
            rotation += self.image_rotation_deg
        return rotation % 360.0

    def _outline_macro_flash_points(
        self,
        aperture: Aperture,
        center: Point,
    ) -> tuple[Point, ...]:
        """Materialize one Code-4 outline flash with exact affine transforms."""

        if not aperture.outline_vertices:
            raise ValueError("outline aperture has no vertices")

        primitive_angle = radians(aperture.outline_rotation_deg)
        primitive_cos = cos(primitive_angle)
        primitive_sin = sin(primitive_angle)
        output_angle = radians(
            (self.aperture_rotation_deg + self.image_rotation_deg) % 360.0
        )
        output_cos = cos(output_angle)
        output_sin = sin(output_angle)

        points: list[Point] = []
        for source_x, source_y in aperture.outline_vertices:
            # Macro primitive rotation precedes the modal LM/LR/LS aperture
            # transform. Legacy MI/SF affect coordinate data, not apertures;
            # whole-image IR rotates both the flash center and local geometry.
            x = source_x * primitive_cos - source_y * primitive_sin
            y = source_x * primitive_sin + source_y * primitive_cos

            if "X" in self.aperture_mirror:
                x = -x
            if "Y" in self.aperture_mirror:
                y = -y

            x *= self.aperture_scale
            y *= self.aperture_scale

            rotated_x = x * output_cos - y * output_sin
            rotated_y = x * output_sin + y * output_cos
            points.append(Point(center.x + rotated_x, center.y + rotated_y))

        return tuple(points)

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
        except (ValueError, SyntaxError, ZeroDivisionError, OverflowError) as exc:
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

        if len(evaluated) != 1:
            self._fail_or_warn(
                path,
                line_no,
                line,
                "UNSUPPORTED_GERBER_APERTURE_MACRO",
                f"aperture macro {name!r} contains multiple primitives",
                out,
            )
            self.unsupported_apertures.add(code)
            return

        primitive = evaluated[0]
        values = primitive["values"]

        if primitive["kind"] == "circle":
            if len(values) not in {4, 5}:
                self._fail_or_warn(
                    path,
                    line_no,
                    line,
                    "INVALID_GERBER_APERTURE_MACRO",
                    f"circle aperture macro {name!r} requires four or five modifiers",
                    out,
                )
                self.unsupported_apertures.add(code)
                return

            exposure, diameter, center_x, center_y = values[:4]
            rotation = values[4] if len(values) == 5 else 0.0
            if not all(
                isfinite(float(value))
                for value in (exposure, diameter, center_x, center_y, rotation)
            ):
                self._fail_or_warn(
                    path,
                    line_no,
                    line,
                    "INVALID_GERBER_APERTURE_MACRO",
                    f"circle aperture macro {name!r} requires finite modifiers",
                    out,
                )
                self.unsupported_apertures.add(code)
                return

            if (
                exposure != 1
                or diameter <= 0
                or abs(center_x) > 1e-12
                or abs(center_y) > 1e-12
            ):
                self._fail_or_warn(
                    path,
                    line_no,
                    line,
                    "UNSUPPORTED_GERBER_APERTURE_MACRO",
                    (
                        f"aperture macro {name!r} requires positive exposure/diameter "
                        "and origin-centered geometry; rotation is immaterial for a "
                        "centered circle"
                    ),
                    out,
                )
                self.unsupported_apertures.add(code)
                return

            diameter_mm = to_mm(float(diameter), self.units)
            if not isfinite(diameter_mm):
                self._fail_or_warn(
                    path,
                    line_no,
                    line,
                    "INVALID_GERBER_APERTURE_MACRO",
                    f"circle aperture macro {name!r} overflows after active-unit conversion",
                    out,
                )
                self.unsupported_apertures.add(code)
                return

            self.apertures[code] = Aperture(code, "C", diameter_mm, diameter_mm)
            return

        if primitive["kind"] == "vector_line":
            if len(values) != 7:
                self._fail_or_warn(
                    path,
                    line_no,
                    line,
                    "INVALID_GERBER_APERTURE_MACRO",
                    f"vector-line aperture macro {name!r} requires seven modifiers",
                    out,
                )
                self.unsupported_apertures.add(code)
                return

            exposure, width, start_x, start_y, end_x, end_y, rotation = values
            epsilon = 1e-12
            midpoint_x = (start_x + end_x) / 2.0
            midpoint_y = (start_y + end_y) / 2.0
            dx = end_x - start_x
            dy = end_y - start_y
            segment_length = hypot(dx, dy)
            finite_values = all(
                isfinite(float(value))
                for value in (
                    exposure,
                    width,
                    start_x,
                    start_y,
                    end_x,
                    end_y,
                    rotation,
                )
            )
            if (
                not finite_values
                or exposure != 1
                or width <= 0
                or abs(midpoint_x) > epsilon
                or abs(midpoint_y) > epsilon
                or segment_length <= epsilon
            ):
                self._fail_or_warn(
                    path,
                    line_no,
                    line,
                    "UNSUPPORTED_GERBER_APERTURE_MACRO",
                    (
                        f"vector-line aperture macro {name!r} requires finite positive "
                        "exposure/width and a non-zero segment whose midpoint is the "
                        "macro origin"
                    ),
                    out,
                )
                self.unsupported_apertures.add(code)
                return

            base_rotation = degrees(atan2(dy, dx)) + rotation
            self.apertures[code] = Aperture(
                code,
                "R",
                to_mm(float(segment_length), self.units),
                to_mm(float(width), self.units),
                base_rotation_deg=base_rotation % 360.0,
            )
            return

        if primitive["kind"] == "center_line":
            if len(values) != 6:
                self._fail_or_warn(
                    path,
                    line_no,
                    line,
                    "INVALID_GERBER_APERTURE_MACRO",
                    f"center-line aperture macro {name!r} requires six modifiers",
                    out,
                )
                self.unsupported_apertures.add(code)
                return

            exposure, width, height, center_x, center_y, rotation = values
            finite_values = all(
                isfinite(float(value))
                for value in (exposure, width, height, center_x, center_y, rotation)
            )
            if (
                not finite_values
                or exposure != 1
                or width <= 0
                or height <= 0
                or abs(center_x) > 1e-12
                or abs(center_y) > 1e-12
            ):
                self._fail_or_warn(
                    path,
                    line_no,
                    line,
                    "UNSUPPORTED_GERBER_APERTURE_MACRO",
                    (
                        f"center-line aperture macro {name!r} requires finite positive "
                        "exposure/size and origin-centered geometry"
                    ),
                    out,
                )
                self.unsupported_apertures.add(code)
                return

            self.apertures[code] = Aperture(
                code,
                "R",
                to_mm(float(width), self.units),
                to_mm(float(height), self.units),
                base_rotation_deg=float(rotation) % 360.0,
            )
            return

        if primitive["kind"] == "outline":
            if len(values) < 2:
                self._fail_or_warn(
                    path,
                    line_no,
                    line,
                    "INVALID_GERBER_APERTURE_MACRO",
                    f"outline aperture macro {name!r} has too few modifiers",
                    out,
                )
                self.unsupported_apertures.add(code)
                return

            exposure, vertices_value = values[:2]
            if (
                not isfinite(float(vertices_value))
                or not float(vertices_value).is_integer()
                or not 3 <= int(vertices_value) <= 5000
            ):
                self._fail_or_warn(
                    path,
                    line_no,
                    line,
                    "INVALID_GERBER_APERTURE_MACRO",
                    (
                        f"outline aperture macro {name!r} requires an integer "
                        "vertex count in 3..5000"
                    ),
                    out,
                )
                self.unsupported_apertures.add(code)
                return

            vertex_count = int(vertices_value)
            expected_values = 2 * vertex_count + 5
            if len(values) != expected_values:
                self._fail_or_warn(
                    path,
                    line_no,
                    line,
                    "INVALID_GERBER_APERTURE_MACRO",
                    (
                        f"outline aperture macro {name!r} declares {vertex_count} "
                        f"vertices but has {len(values)} modifiers; expected "
                        f"{expected_values}"
                    ),
                    out,
                )
                self.unsupported_apertures.add(code)
                return

            if not all(isfinite(float(value)) for value in values):
                self._fail_or_warn(
                    path,
                    line_no,
                    line,
                    "INVALID_GERBER_APERTURE_MACRO",
                    f"outline aperture macro {name!r} contains non-finite values",
                    out,
                )
                self.unsupported_apertures.add(code)
                return

            rotation = float(values[-1])
            coordinates = [float(value) for value in values[2:-1]]
            points = [
                (coordinates[index], coordinates[index + 1])
                for index in range(0, len(coordinates), 2)
            ]
            epsilon = 1e-12
            if exposure != 1 or points[-1] != points[0]:
                self._fail_or_warn(
                    path,
                    line_no,
                    line,
                    "UNSUPPORTED_GERBER_APERTURE_MACRO",
                    (
                        f"outline aperture macro {name!r} requires additive "
                        "exposure and an explicitly closed contour whose last "
                        "vertex exactly equals its start vertex"
                    ),
                    out,
                )
                self.unsupported_apertures.add(code)
                return

            vertices = points[:-1]

            if vertex_count == 4:
                edges = [
                    (
                        vertices[(index + 1) % 4][0] - vertices[index][0],
                        vertices[(index + 1) % 4][1] - vertices[index][1],
                    )
                    for index in range(4)
                ]
                lengths = [hypot(dx, dy) for dx, dy in edges]
                centered = (
                    isclose(
                        vertices[0][0],
                        -vertices[2][0],
                        rel_tol=1e-9,
                        abs_tol=epsilon,
                    )
                    and isclose(
                        vertices[0][1],
                        -vertices[2][1],
                        rel_tol=1e-9,
                        abs_tol=epsilon,
                    )
                    and isclose(
                        vertices[1][0],
                        -vertices[3][0],
                        rel_tol=1e-9,
                        abs_tol=epsilon,
                    )
                    and isclose(
                        vertices[1][1],
                        -vertices[3][1],
                        rel_tol=1e-9,
                        abs_tol=epsilon,
                    )
                )
                opposite_edges = (
                    isclose(edges[0][0], -edges[2][0], rel_tol=1e-9, abs_tol=epsilon)
                    and isclose(
                        edges[0][1], -edges[2][1], rel_tol=1e-9, abs_tol=epsilon
                    )
                    and isclose(
                        edges[1][0], -edges[3][0], rel_tol=1e-9, abs_tol=epsilon
                    )
                    and isclose(
                        edges[1][1], -edges[3][1], rel_tol=1e-9, abs_tol=epsilon
                    )
                )
                adjacent_dot = edges[0][0] * edges[1][0] + edges[0][1] * edges[1][1]
                orthogonal = (
                    lengths[0] > epsilon
                    and lengths[1] > epsilon
                    and abs(adjacent_dot)
                    <= 1e-9 * lengths[0] * lengths[1] + epsilon
                )
                if centered and opposite_edges and orthogonal:
                    base_rotation = (
                        degrees(atan2(edges[0][1], edges[0][0])) + rotation
                    ) % 360.0
                    self.apertures[code] = Aperture(
                        code,
                        "R",
                        to_mm(lengths[0], self.units),
                        to_mm(lengths[1], self.units),
                        base_rotation_deg=base_rotation,
                    )
                    return

            if 3 <= vertex_count <= 12:
                radii = [hypot(x, y) for x, y in vertices]
                radius = radii[0]
                regular = radius > epsilon and all(
                    isclose(
                        candidate,
                        radius,
                        rel_tol=1e-9,
                        abs_tol=epsilon,
                    )
                    for candidate in radii[1:]
                )
                if regular:
                    expected_dot = cos(2.0 * pi / vertex_count)
                    expected_cross = abs(sin(2.0 * pi / vertex_count))
                    orientation = 0
                    for index in range(vertex_count):
                        x0, y0 = vertices[index]
                        x1, y1 = vertices[(index + 1) % vertex_count]
                        denominator = radii[index] * radii[(index + 1) % vertex_count]
                        normalized_dot = (x0 * x1 + y0 * y1) / denominator
                        normalized_cross = (x0 * y1 - y0 * x1) / denominator
                        if (
                            not isclose(
                                normalized_dot,
                                expected_dot,
                                rel_tol=1e-9,
                                abs_tol=1e-9,
                            )
                            or not isclose(
                                abs(normalized_cross),
                                expected_cross,
                                rel_tol=1e-9,
                                abs_tol=1e-9,
                            )
                            or abs(normalized_cross) <= epsilon
                        ):
                            regular = False
                            break
                        current_orientation = 1 if normalized_cross > 0 else -1
                        if orientation == 0:
                            orientation = current_orientation
                        elif current_orientation != orientation:
                            regular = False
                            break

                if regular:
                    polygon_rotation = (
                        degrees(atan2(vertices[0][1], vertices[0][0])) + rotation
                    ) % 360.0
                    diameter_mm = to_mm(2.0 * radius, self.units)
                    self.apertures[code] = Aperture(
                        code,
                        "P",
                        diameter_mm,
                        diameter_mm,
                        polygon_vertices=vertex_count,
                        polygon_rotation_deg=polygon_rotation,
                    )
                    return

            segment_scale = max(
                1.0,
                *(abs(coordinate) for point in vertices for coordinate in point),
            )
            minimum_segment_length = 1e-12 * segment_scale
            if any(
                hypot(
                    vertices[(index + 1) % vertex_count][0] - vertices[index][0],
                    vertices[(index + 1) % vertex_count][1] - vertices[index][1],
                )
                <= minimum_segment_length
                for index in range(vertex_count)
            ):
                self._fail_or_warn(
                    path,
                    line_no,
                    line,
                    "INVALID_GERBER_APERTURE_MACRO",
                    (
                        f"outline aperture macro {name!r} contains a zero-length "
                        "contour segment"
                    ),
                    out,
                )
                self.unsupported_apertures.add(code)
                return

            vertices_mm = tuple(
                (to_mm(x, self.units), to_mm(y, self.units))
                for x, y in vertices
            )
            if any(
                not isfinite(coordinate)
                for point in vertices_mm
                for coordinate in point
            ):
                self._fail_or_warn(
                    path,
                    line_no,
                    line,
                    "INVALID_GERBER_APERTURE_MACRO",
                    (
                        f"outline aperture macro {name!r} overflows after active-unit "
                        "conversion"
                    ),
                    out,
                )
                self.unsupported_apertures.add(code)
                return

            outline_polygon = Polygon(vertices_mm)
            if (
                outline_polygon.is_empty
                or not outline_polygon.is_valid
                or outline_polygon.area <= 0.0
            ):
                self._fail_or_warn(
                    path,
                    line_no,
                    line,
                    "INVALID_GERBER_APERTURE_MACRO",
                    (
                        f"outline aperture macro {name!r} must define one simple, "
                        "non-self-touching, non-zero-area contour"
                    ),
                    out,
                )
                self.unsupported_apertures.add(code)
                return

            self.apertures[code] = Aperture(
                code,
                "AM4",
                0.0,
                0.0,
                outline_vertices=vertices_mm,
                outline_rotation_deg=rotation % 360.0,
            )
            return

        if primitive["kind"] == "polygon":
            if len(values) != 6:
                self._fail_or_warn(
                    path,
                    line_no,
                    line,
                    "INVALID_GERBER_APERTURE_MACRO",
                    f"polygon aperture macro {name!r} requires six modifiers",
                    out,
                )
                self.unsupported_apertures.add(code)
                return

            exposure, vertices_value, center_x, center_y, diameter, rotation = values
            epsilon = 1e-12
            if (
                exposure != 1
                or not isfinite(vertices_value)
                or not float(vertices_value).is_integer()
                or not 3 <= int(vertices_value) <= 12
                or not isfinite(center_x)
                or not isfinite(center_y)
                or not isfinite(diameter)
                or diameter <= 0
                or abs(center_x) > epsilon
                or abs(center_y) > epsilon
                or not isfinite(rotation)
            ):
                self._fail_or_warn(
                    path,
                    line_no,
                    line,
                    "UNSUPPORTED_GERBER_APERTURE_MACRO",
                    (
                        f"polygon aperture macro {name!r} requires positive "
                        "exposure/diameter, an integer vertex count in 3..12, "
                        "origin-centered geometry, and finite rotation"
                    ),
                    out,
                )
                self.unsupported_apertures.add(code)
                return

            diameter_mm = to_mm(float(diameter), self.units)
            self.apertures[code] = Aperture(
                code,
                "P",
                diameter_mm,
                diameter_mm,
                polygon_vertices=int(vertices_value),
                polygon_rotation_deg=float(rotation) % 360.0,
            )
            return

        if primitive["kind"] == "lower_left_line":
            if len(values) != 6:
                self._fail_or_warn(
                    path,
                    line_no,
                    line,
                    "INVALID_GERBER_APERTURE_MACRO",
                    f"lower-left aperture macro {name!r} requires six modifiers",
                    out,
                )
                self.unsupported_apertures.add(code)
                return

            exposure, width, height, lower_left_x, lower_left_y, rotation = values
            center_x = lower_left_x + width / 2.0
            center_y = lower_left_y + height / 2.0
            finite_values = all(
                isfinite(float(value))
                for value in (
                    exposure,
                    width,
                    height,
                    lower_left_x,
                    lower_left_y,
                    rotation,
                )
            )
            if (
                not finite_values
                or exposure != 1
                or width <= 0
                or height <= 0
                or abs(center_x) > 1e-12
                or abs(center_y) > 1e-12
            ):
                self._fail_or_warn(
                    path,
                    line_no,
                    line,
                    "UNSUPPORTED_GERBER_APERTURE_MACRO",
                    (
                        f"lower-left aperture macro {name!r} requires finite positive "
                        "exposure/size and a rectangle centered on the macro origin"
                    ),
                    out,
                )
                self.unsupported_apertures.add(code)
                return

            self.apertures[code] = Aperture(
                code,
                "R",
                to_mm(float(width), self.units),
                to_mm(float(height), self.units),
                base_rotation_deg=float(rotation) % 360.0,
            )
            return

        self._fail_or_warn(
            path,
            line_no,
            line,
            "UNSUPPORTED_GERBER_APERTURE_MACRO",
            (
                f"aperture macro {name!r} primitive {primitive['kind']!r} "
                "is not implemented in the production geometry path"
            ),
            out,
        )
        self.unsupported_apertures.add(code)

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
            output_offset = self._rotate_image_point(Point(dx_mm, dy_mm))
            detail = (
                f"instance=({x_index + 1},{y_index + 1})/"
                f"({self.step_repeat.x_count},{self.step_repeat.y_count});"
                f" source_offset_mm=({dx_mm:.12g},{dy_mm:.12g})"
            )
            if self.image_rotation_deg:
                detail += (
                    f"; output_offset_mm=({output_offset.x:.12g},"
                    f"{output_offset.y:.12g})"
                )
            prov.add_evidence(
                Evidence(
                    "gerber_step_repeat",
                    detail,
                    1.0,
                    src,
                )
            )
        if self.mirror_image_source is not None and (self.mirror_a or self.mirror_b):
            prov.add_source(self.mirror_image_source)
            prov.add_evidence(
                Evidence(
                    "gerber_mirror_image",
                    f"mirror_a={int(self.mirror_a)}; mirror_b={int(self.mirror_b)}",
                    1.0,
                    self.mirror_image_source,
                )
            )
        if self.scale_source is not None and (
            not isclose(self.scale_a, 1.0, rel_tol=0.0, abs_tol=1e-12)
            or not isclose(self.scale_b, 1.0, rel_tol=0.0, abs_tol=1e-12)
        ):
            prov.add_source(self.scale_source)
            prov.add_evidence(
                Evidence(
                    "gerber_scale_factor",
                    f"scale_a={self.scale_a:.12g}; scale_b={self.scale_b:.12g}",
                    1.0,
                    self.scale_source,
                )
            )
        if self.offset_source is not None and (self.offset_a_mm or self.offset_b_mm):
            prov.add_source(self.offset_source)
            prov.add_evidence(
                Evidence(
                    "gerber_image_offset",
                    (
                        f"offset_mm=({self.offset_a_mm:.12g},"
                        f"{self.offset_b_mm:.12g})"
                    ),
                    1.0,
                    self.offset_source,
                )
            )
        if self.image_rotation_source is not None and self.image_rotation_deg:
            prov.add_source(self.image_rotation_source)
            prov.add_evidence(
                Evidence(
                    "gerber_image_rotation",
                    f"rotation_deg_ccw={self.image_rotation_deg}",
                    1.0,
                    self.image_rotation_source,
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
            if not self.strict:
                self._disable_image_geometry(out)
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
            if not self.strict:
                self._disable_image_geometry(out)
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
            if not self.strict:
                self._disable_image_geometry(out)
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

    def _abort_region(self) -> None:
        self.region_state.abort()
        self.region_sources.clear()
        self.region_arc_evidence.clear()
        self.region_contours.clear()
        self.region_contour_holes.clear()
        self.region_contour_sources.clear()
        self.region_contour_arc_evidence.clear()
        self.region_contour_cutin_evidence.clear()
        self.region_current_sources.clear()
        self.region_current_arc_evidence.clear()
        self.region_current_edge_kinds.clear()
        self.region_start_line = None

    def _region_fail(
        self,
        path: Path,
        line_no: int,
        raw: str,
        code: str,
        message: str,
        out: GerberLayerResult,
    ) -> None:
        self._fail_or_warn(path, line_no, raw, code, message, out)
        self._abort_region()

    def _region_parse_fail(
        self,
        path: Path,
        line_no: int,
        raw: str,
        code: str,
        message: str,
        out: GerberLayerResult,
    ) -> None:
        self._parse_error_or_warn(path, line_no, raw, code, message, out)
        self._abort_region()

    def _begin_region(
        self,
        path: Path,
        line_no: int,
        line: str,
        out: GerberLayerResult,
    ) -> None:
        if self.layer == "Edge.Cuts":
            self._fail_or_warn(
                path,
                line_no,
                line,
                "GERBER_REGION_EDGE_CUTS_UNSUPPORTED",
                "filled Gerber regions are not supported on Edge.Cuts",
                out,
            )
            return
        if self.region_state.active:
            self._region_fail(
                path,
                line_no,
                line,
                "GERBER_REGION_NESTED",
                "nested G36 region start is invalid",
                out,
            )
            return
        self.region_state.begin()
        self.region_sources = [SourceRef(str(path), line_no, line)]
        self.region_arc_evidence = []
        self.region_contours = []
        self.region_contour_holes = []
        self.region_contour_sources = []
        self.region_contour_arc_evidence = []
        self.region_contour_cutin_evidence = []
        self.region_current_sources = []
        self.region_current_arc_evidence = []
        self.region_current_edge_kinds = []
        self.region_start_line = line_no

    def _finish_current_region_contour(
        self,
        path: Path,
        line_no: int,
        raw: str,
        out: GerberLayerResult,
        *,
        reason: str,
    ) -> bool:
        raw_vertices = tuple(self.region_state.vertices)
        if not raw_vertices:
            self._region_parse_fail(
                path,
                line_no,
                raw,
                "GERBER_REGION_EMPTY_CONTOUR",
                f"{reason} cannot finalize an empty region contour",
                out,
            )
            return False

        points = [Point(float(x), float(y)) for x, y in raw_vertices]
        first = points[0]
        last = points[-1]
        closure_tol_mm = 1e-9
        if not (
            isclose(first.x, last.x, rel_tol=0.0, abs_tol=closure_tol_mm)
            and isclose(first.y, last.y, rel_tol=0.0, abs_tol=closure_tol_mm)
        ):
            message = (
                "G37 does not implicitly close a region contour; "
                "final point must coincide with its first point"
                if reason == "G37"
                else (
                    f"{reason} cannot finalize an open region contour; "
                    "final point must coincide with its first point"
                )
            )
            self._region_parse_fail(
                path,
                line_no,
                raw,
                "GERBER_REGION_NOT_CLOSED",
                message,
                out,
            )
            return False
        if last != first:
            points[-1] = first

        if any(a == b for a, b in zip(points, points[1:])):
            self._region_parse_fail(
                path,
                line_no,
                raw,
                "GERBER_REGION_ZERO_LENGTH_SEGMENT",
                "zero-length contour segments are not valid",
                out,
            )
            return False

        if len(self.region_current_edge_kinds) != len(points) - 1:
            self._region_parse_fail(
                path,
                line_no,
                raw,
                "GERBER_REGION_EDGE_STATE_INVALID",
                "internal region edge classification does not match contour segments",
                out,
            )
            return False

        unique = {(point.x, point.y) for point in points[:-1]}
        if len(unique) < 3:
            self._region_parse_fail(
                path,
                line_no,
                raw,
                "GERBER_REGION_VERTEX_COUNT_INVALID",
                "region contour needs at least three unique vertices",
                out,
            )
            return False

        undirected_edges: dict[
            tuple[tuple[float, float], tuple[float, float]],
            list[tuple[int, Point, Point]],
        ] = {}
        for edge_index, (edge_start, edge_end) in enumerate(
            zip(points, points[1:])
        ):
            a = (edge_start.x, edge_start.y)
            b = (edge_end.x, edge_end.y)
            key = (a, b) if a <= b else (b, a)
            undirected_edges.setdefault(key, []).append(
                (edge_index, edge_start, edge_end)
            )
        coincident_edges = [
            uses for uses in undirected_edges.values() if len(uses) > 1
        ]

        shell = tuple(points)
        holes: tuple[tuple[Point, ...], ...] = ()
        cutin_evidence: list[Evidence] = []

        if coincident_edges:
            bridge_pairs: list[
                tuple[int, int, Point, Point, str]
            ] = []
            bridge_indices: set[int] = set()
            bridge_axes: set[str] = set()

            for uses in coincident_edges:
                if len(uses) != 2:
                    self._region_parse_fail(
                        path,
                        line_no,
                        raw,
                        "GERBER_REGION_CUTIN_INVALID",
                        "each cut-in bridge must occur exactly twice",
                        out,
                    )
                    return False

                first_use, second_use = sorted(uses, key=lambda item: item[0])
                i, a0, a1 = first_use
                j, b0, b1 = second_use
                reversed_pair = a0 == b1 and a1 == b0
                horizontal = isclose(
                    a0.y,
                    a1.y,
                    rel_tol=0.0,
                    abs_tol=1e-12,
                )
                vertical = isclose(
                    a0.x,
                    a1.x,
                    rel_tol=0.0,
                    abs_tol=1e-12,
                )
                bridge_is_linear = (
                    self.region_current_edge_kinds[i] == "linear"
                    and self.region_current_edge_kinds[j] == "linear"
                )
                if (
                    not reversed_pair
                    or not bridge_is_linear
                    or horizontal == vertical
                ):
                    self._region_parse_fail(
                        path,
                        line_no,
                        raw,
                        "GERBER_REGION_CUTIN_INVALID",
                        (
                            "cut-in requires two opposite fully-coincident "
                            "linear segments that are strictly horizontal or "
                            "vertical"
                        ),
                        out,
                    )
                    return False

                axis = "horizontal" if horizontal else "vertical"
                bridge_axes.add(axis)
                bridge_indices.update((i, j))
                bridge_pairs.append((i, j, a0, a1, axis))

            if len(bridge_axes) != 1:
                self._region_parse_fail(
                    path,
                    line_no,
                    raw,
                    "GERBER_REGION_CUTIN_DIRECTION_MISMATCH",
                    (
                        "all cut-ins in one Gerber contour must have the same "
                        "direction, either all horizontal or all vertical"
                    ),
                    out,
                )
                return False

            edges = list(enumerate(zip(points, points[1:])))
            adjacency: dict[
                tuple[float, float],
                list[tuple[tuple[float, float], int]],
            ] = {}
            edge_coords: dict[
                int,
                tuple[tuple[float, float], tuple[float, float]],
            ] = {}
            for edge_index, (edge_start, edge_end) in edges:
                if edge_index in bridge_indices:
                    continue
                start_key = (edge_start.x, edge_start.y)
                end_key = (edge_end.x, edge_end.y)
                edge_coords[edge_index] = (start_key, end_key)
                adjacency.setdefault(start_key, []).append(
                    (end_key, edge_index)
                )
                adjacency.setdefault(end_key, []).append(
                    (start_key, edge_index)
                )

            if not edge_coords or any(
                len(neighbors) != 2 for neighbors in adjacency.values()
            ):
                self._region_parse_fail(
                    path,
                    line_no,
                    raw,
                    "GERBER_REGION_CUTIN_INVALID",
                    (
                        "removing cut-in bridges must leave disjoint closed "
                        "boundary cycles without self-touching vertices"
                    ),
                    out,
                )
                return False

            unvisited = set(edge_coords)
            loops: list[tuple[Point, ...]] = []
            while unvisited:
                first_edge = min(unvisited)
                start_key, current_key = edge_coords[first_edge]
                ring_keys = [start_key, current_key]
                unvisited.remove(first_edge)
                previous_edge = first_edge

                while current_key != start_key:
                    candidates = [
                        (neighbor_key, edge_index)
                        for neighbor_key, edge_index in adjacency[current_key]
                        if edge_index in unvisited
                        and edge_index != previous_edge
                    ]
                    if len(candidates) != 1:
                        self._region_parse_fail(
                            path,
                            line_no,
                            raw,
                            "GERBER_REGION_CUTIN_INVALID",
                            (
                                "cut-in bridge removal produced ambiguous or "
                                "open boundary topology"
                            ),
                            out,
                        )
                        return False
                    next_key, next_edge = candidates[0]
                    ring_keys.append(next_key)
                    unvisited.remove(next_edge)
                    previous_edge = next_edge
                    current_key = next_key

                ring = tuple(Point(x, y) for x, y in ring_keys)
                if len(ring) < 4 or ring[0] != ring[-1]:
                    self._region_parse_fail(
                        path,
                        line_no,
                        raw,
                        "GERBER_REGION_CUTIN_INVALID",
                        "cut-in boundary cycle is not a valid closed ring",
                        out,
                    )
                    return False
                loops.append(ring)

            if len(loops) != len(bridge_pairs) + 1:
                self._region_parse_fail(
                    path,
                    line_no,
                    raw,
                    "GERBER_REGION_CUTIN_INVALID",
                    (
                        "cut-in decomposition did not produce exactly one "
                        "boundary loop per cut-in plus the enclosing contour"
                    ),
                    out,
                )
                return False

            loop_shapes = []
            loop_signed_areas: list[float] = []
            for loop_index, ring in enumerate(loops):
                ring_unique = {(p.x, p.y) for p in ring[:-1]}
                if len(ring_unique) < 3:
                    self._region_parse_fail(
                        path,
                        line_no,
                        raw,
                        "GERBER_REGION_CUTIN_INVALID",
                        f"cut-in boundary loop {loop_index + 1} is degenerate",
                        out,
                    )
                    return False
                ring_region = CopperRegion(
                    "validation",
                    ring,
                    self.layer,
                )
                ring_shape = region_shape(ring_region)
                if (
                    ring_shape.is_empty
                    or float(ring_shape.area) <= 0
                    or not ring_shape.is_valid
                ):
                    self._region_parse_fail(
                        path,
                        line_no,
                        raw,
                        "GERBER_REGION_CUTIN_INVALID",
                        (
                            f"cut-in boundary loop {loop_index + 1} is "
                            "self-intersecting or otherwise invalid"
                        ),
                        out,
                    )
                    return False
                signed_area = 0.5 * sum(
                    a.x * b.y - b.x * a.y
                    for a, b in zip(ring, ring[1:])
                )
                if isclose(signed_area, 0.0, rel_tol=0.0, abs_tol=1e-15):
                    self._region_parse_fail(
                        path,
                        line_no,
                        raw,
                        "GERBER_REGION_CUTIN_INVALID",
                        f"cut-in boundary loop {loop_index + 1} has zero signed area",
                        out,
                    )
                    return False
                loop_shapes.append(ring_shape)
                loop_signed_areas.append(signed_area)

            top_level = [
                index
                for index, candidate_shape in enumerate(loop_shapes)
                if not any(
                    other_index != index
                    and loop_shapes[other_index].contains(candidate_shape)
                    for other_index in range(len(loop_shapes))
                )
            ]
            if len(top_level) != 1:
                self._region_fail(
                    path,
                    line_no,
                    raw,
                    "GERBER_REGION_CUTIN_DISJOINT_UNSUPPORTED",
                    (
                        "fully-coincident cut-in topology resolves to multiple "
                        "top-level filled areas rather than one enclosing "
                        "region; disjoint cut-in output is not modeled yet"
                    ),
                    out,
                )
                return False

            shell_index = top_level[0]
            shell = loops[shell_index]
            shell_shape = loop_shapes[shell_index]
            shell_sign = 1.0 if loop_signed_areas[shell_index] > 0 else -1.0
            hole_indices = [
                index for index in range(len(loops))
                if index != shell_index
            ]

            for hole_index in hole_indices:
                hole_shape = loop_shapes[hole_index]
                if not shell_shape.contains(hole_shape):
                    self._region_parse_fail(
                        path,
                        line_no,
                        raw,
                        "GERBER_REGION_CUTIN_INVALID",
                        "every cut-in hole must be strictly inside one shell",
                        out,
                    )
                    return False
                hole_sign = 1.0 if loop_signed_areas[hole_index] > 0 else -1.0
                if hole_sign == shell_sign:
                    self._region_parse_fail(
                        path,
                        line_no,
                        raw,
                        "GERBER_REGION_CUTIN_WINDING_INVALID",
                        (
                            "cut-in hole traversal must have the opposite "
                            "winding from the enclosing boundary"
                        ),
                        out,
                    )
                    return False

            for pos, left_index in enumerate(hole_indices):
                for right_index in hole_indices[pos + 1 :]:
                    if not loop_shapes[left_index].disjoint(
                        loop_shapes[right_index]
                    ):
                        self._region_parse_fail(
                            path,
                            line_no,
                            raw,
                            "GERBER_REGION_CUTIN_INVALID",
                            "cut-in holes may not touch, overlap, or nest",
                            out,
                        )
                        return False

            boundary_union = unary_union(
                [loop_shapes[index].boundary for index in range(len(loops))]
            )
            bridge_lines = []
            for _, _, bridge_start, bridge_end, _ in bridge_pairs:
                bridge_line = LineString(
                    [
                        (bridge_start.x, bridge_start.y),
                        (bridge_end.x, bridge_end.y),
                    ]
                )
                expected_contacts = MultiPoint(
                    [
                        (bridge_start.x, bridge_start.y),
                        (bridge_end.x, bridge_end.y),
                    ]
                )
                contacts = bridge_line.intersection(boundary_union)
                if not contacts.equals(expected_contacts):
                    self._region_parse_fail(
                        path,
                        line_no,
                        raw,
                        "GERBER_REGION_CUTIN_TOUCH_INVALID",
                        (
                            "cut-in bridge may touch or overlap contour "
                            "boundaries only at its start and end points"
                        ),
                        out,
                    )
                    return False
                if not shell_shape.covers(bridge_line):
                    self._region_parse_fail(
                        path,
                        line_no,
                        raw,
                        "GERBER_REGION_CUTIN_INVALID",
                        "cut-in bridge must remain inside the enclosing contour",
                        out,
                    )
                    return False
                bridge_lines.append(bridge_line)

            for bridge_index, left_line in enumerate(bridge_lines):
                for right_line in bridge_lines[bridge_index + 1 :]:
                    if not left_line.intersection(right_line).is_empty:
                        self._region_parse_fail(
                            path,
                            line_no,
                            raw,
                            "GERBER_REGION_CUTIN_TOUCH_INVALID",
                            "cut-in bridges may not touch or intersect each other",
                            out,
                        )
                        return False

            holes = tuple(loops[index] for index in hole_indices)
            candidate = CopperRegion(
                "validation",
                shell,
                self.layer,
                holes=holes,
            )
            shape = region_shape(candidate)
            if shape.is_empty or float(shape.area) <= 0 or not shape.is_valid:
                self._region_parse_fail(
                    path,
                    line_no,
                    raw,
                    "GERBER_REGION_CUTIN_INVALID",
                    (
                        "multi-cut-in shell/hole reconstruction produced "
                        "invalid polygon geometry"
                    ),
                    out,
                )
                return False

            evidence_source = (
                self.region_current_sources[-1]
                if self.region_current_sources
                else SourceRef(str(path), line_no, raw)
            )
            for bridge_index, (
                _,
                _,
                bridge_start,
                bridge_end,
                bridge_axis,
            ) in enumerate(bridge_pairs):
                cutin_evidence.append(
                    Evidence(
                        "gerber_region_cut_in",
                        (
                            f"cut_in={bridge_index + 1}/{len(bridge_pairs)}; "
                            f"bridge_orientation={bridge_axis}; "
                            f"bridge_start_mm=({bridge_start.x:.12g},{bridge_start.y:.12g}); "
                            f"bridge_end_mm=({bridge_end.x:.12g},{bridge_end.y:.12g}); "
                            f"holes={len(holes)}; "
                            f"filled_area_mm2={float(shape.area):.12g}"
                        ),
                        1.0,
                        evidence_source,
                    )
                )
        else:
            candidate = CopperRegion(
                "validation",
                shell,
                self.layer,
                provenance=Provenance(),
            )
            shape = region_shape(candidate)
            if shape.is_empty or float(shape.area) <= 0 or not shape.is_valid:
                self._region_parse_fail(
                    path,
                    line_no,
                    raw,
                    "GERBER_REGION_CONTOUR_INVALID",
                    (
                        "region contour is empty, zero-area, self-touching, "
                        "or self-intersecting"
                    ),
                    out,
                )
                return False

        self.region_contours.append(shell)
        self.region_contour_holes.append(holes)
        self.region_contour_sources.append(list(self.region_current_sources))
        self.region_contour_arc_evidence.append(
            list(self.region_current_arc_evidence)
        )
        self.region_contour_cutin_evidence.append(cutin_evidence)
        self.region_state.vertices.clear()
        self.region_current_sources.clear()
        self.region_current_arc_evidence.clear()
        self.region_current_edge_kinds.clear()
        return True

    def _region_coordinate(
        self,
        path: Path,
        line_no: int,
        line: str,
        out: GerberLayerResult,
        x_raw: str | None,
        y_raw: str | None,
        op: str | None,
    ) -> None:
        operation = op or self.current_operation
        if op is not None:
            self.current_operation = op
        nxt = self._coordinate_point(x_raw, y_raw)
        self.image_body_started = True
        src = SourceRef(str(path), line_no, line)

        if operation == "2":
            if self.region_state.vertices:
                if not self._finish_current_region_contour(
                    path,
                    line_no,
                    line,
                    out,
                    reason="D02",
                ):
                    self.current = nxt
                    return
            self.region_state.add(nxt.x, nxt.y)
            self.region_current_sources.append(src)
            self.region_sources.append(src)
            self.current = nxt
            return

        if operation == "1":
            if self.interpolation != "linear":
                self._region_fail(
                    path,
                    line_no,
                    line,
                    "GERBER_REGION_ARC_DISPATCH_ERROR",
                    "circular region draw reached the linear-region handler",
                    out,
                )
                self.current = nxt
                return
            if not self.region_state.vertices:
                self._region_parse_fail(
                    path,
                    line_no,
                    line,
                    "GERBER_REGION_START_MOVE_REQUIRED",
                    "a region contour must begin with D02 before its first D01 segment",
                    out,
                )
                self.current = nxt
                return
            self.region_state.add(nxt.x, nxt.y)
            self.region_current_edge_kinds.append("linear")
            self.region_current_sources.append(src)
            self.region_sources.append(src)
            self.current = nxt
            return

        if operation == "3":
            self._region_fail(
                path,
                line_no,
                line,
                "GERBER_REGION_FLASH_UNSUPPORTED",
                "D03 flashes are not valid inside a Gerber region statement",
                out,
            )
            self.current = nxt
            return

        self._region_parse_fail(
            path,
            line_no,
            line,
            "GERBER_REGION_DCODE_REQUIRED",
            "region coordinates require D01 or D02, either explicit or modal",
            out,
        )
        self.current = nxt

    def _region_arc_coordinate(
        self,
        path: Path,
        line_no: int,
        line: str,
        out: GerberLayerResult,
        x_raw: str | None,
        y_raw: str | None,
        i_raw: str | None,
        j_raw: str | None,
        op: str | None,
    ) -> None:
        operation = op or self.current_operation
        if op is not None:
            self.current_operation = op
        nxt = self._coordinate_point(x_raw, y_raw)
        self.image_body_started = True

        if operation == "2":
            self._region_coordinate(
                path,
                line_no,
                line,
                out,
                x_raw,
                y_raw,
                op,
            )
            return

        if operation != "1":
            self._region_parse_fail(
                path,
                line_no,
                line,
                "GERBER_REGION_ARC_DCODE_REQUIRED",
                "circular region interpolation requires D01",
                out,
            )
            self.current = nxt
            return

        if self.interpolation not in {"cw_arc", "ccw_arc"}:
            self._region_parse_fail(
                path,
                line_no,
                line,
                "GERBER_REGION_ARC_MODE_MISSING",
                "region I/J offsets require active G02 or G03 interpolation",
                out,
            )
            self.current = nxt
            return

        if self.quadrant_mode not in {"single", "multi"}:
            self._region_fail(
                path,
                line_no,
                line,
                "GERBER_REGION_ARC_QUADRANT_UNSUPPORTED",
                "region arcs require explicit G74 or G75 quadrant mode before G36",
                out,
            )
            self.current = nxt
            return

        clockwise = self.interpolation == "cw_arc"
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
            if not self.strict:
                self._abort_region()
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
            output_scale = max(abs(self.scale_a), abs(self.scale_b))
            source_chord_error = _ARC_MAX_CHORD_ERROR_MM / output_scale
            segment_count = segments_for_chord_error(
                spec,
                source_chord_error,
                max_segments=_MAX_ARC_SEGMENTS,
                rel_tol=1e-6,
                abs_tol=radius_tolerance,
            )
            arc_vertices = arc_points(
                spec,
                segments=segment_count,
                rel_tol=1e-6,
                abs_tol=radius_tolerance,
            )
        except ValueError as exc:
            self._region_parse_fail(
                path,
                line_no,
                line,
                "GERBER_REGION_ARC_INVALID",
                f"invalid {self.quadrant_mode.upper()} region arc geometry ({exc})",
                out,
            )
            self.current = nxt
            return

        if not self.region_state.vertices:
            self._region_parse_fail(
                path,
                line_no,
                line,
                "GERBER_REGION_START_MOVE_REQUIRED",
                "a region contour must begin with D02 before its first circular D01 segment",
                out,
            )
            self.current = nxt
            return
        for vertex in arc_vertices[1:]:
            self.region_state.add(vertex.x, vertex.y)
            self.region_current_edge_kinds.append("arc")

        src = SourceRef(str(path), line_no, line)
        self.region_current_sources.append(src)
        self.region_sources.append(src)
        arc_evidence = Evidence(
                "gerber_region_arc_tessellation",
                (
                    f"quadrant_mode={self.quadrant_mode}; "
                    f"direction={'CW' if clockwise else 'CCW'}; "
                    f"source_center_mm=({center.x:.12g},{center.y:.12g}); "
                    f"source_radius_mm={radius:.12g}; "
                    f"segments={segment_count}; "
                    f"max_output_chord_error_mm={_ARC_MAX_CHORD_ERROR_MM:.12g}"
                ),
                1.0,
                src,
            )
        self.region_current_arc_evidence.append(arc_evidence)
        self.region_arc_evidence.append(arc_evidence)
        self.current = nxt

    def _end_region(
        self,
        path: Path,
        line_no: int,
        line: str,
        out: GerberLayerResult,
    ) -> None:
        if not self.region_state.active:
            self._parse_error_or_warn(
                path,
                line_no,
                line,
                "GERBER_REGION_END_WITHOUT_START",
                "G37 encountered without an active G36 region",
                out,
            )
            return

        if not self.image_geometry_enabled:
            self._abort_region()
            return

        if not self._finish_current_region_contour(
            path,
            line_no,
            line,
            out,
            reason="G37",
        ):
            return

        self.region_state.end()
        contours = list(self.region_contours)
        contour_holes = list(self.region_contour_holes)
        contour_sources = [list(items) for items in self.region_contour_sources]
        contour_arc_evidence = [
            list(items) for items in self.region_contour_arc_evidence
        ]
        contour_cutin_evidence = [
            list(items) for items in self.region_contour_cutin_evidence
        ]
        statement_start_sources = self.region_sources[:1]
        start_line = self.region_start_line
        end_src = SourceRef(str(path), line_no, line)

        self.region_sources = []
        self.region_arc_evidence = []
        self.region_contours = []
        self.region_contour_holes = []
        self.region_contour_sources = []
        self.region_contour_arc_evidence = []
        self.region_contour_cutin_evidence = []
        self.region_current_sources = []
        self.region_current_arc_evidence = []
        self.region_current_edge_kinds = []
        self.region_start_line = None

        contour_count = len(contours)
        for contour_index, points in enumerate(contours):
            holes = contour_holes[contour_index]
            source_region = CopperRegion(
                "validation",
                points,
                self.layer,
                holes=holes,
            )
            source_shape = region_shape(source_region)
            if (
                source_shape.is_empty
                or float(source_shape.area) <= 0
                or not source_shape.is_valid
            ):
                self._parse_error_or_warn(
                    path,
                    line_no,
                    line,
                    "GERBER_REGION_GEOMETRY_INVALID",
                    (
                        f"contour {contour_index + 1}/{contour_count} is empty, "
                        "zero-area, self-touching, or self-intersecting"
                    ),
                    out,
                )
                return

            coords = tuple((point.x, point.y) for point in points)
            hole_coords = tuple(
                tuple((point.x, point.y) for point in ring)
                for ring in holes
            )
            unique = {(point.x, point.y) for point in points[:-1]}
            sources = [
                *statement_start_sources,
                *contour_sources[contour_index],
                end_src,
            ]
            arc_evidence = contour_arc_evidence[contour_index]
            cutin_evidence = contour_cutin_evidence[contour_index]
            if cutin_evidence:
                region_kind = (
                    f"linear_g75_multi_cutin_{self.layer_polarity}"
                    if arc_evidence
                    else f"linear_multi_cutin_{self.layer_polarity}"
                )
            else:
                region_kind = (
                    f"linear_g75_multi_contour_{self.layer_polarity}"
                    if arc_evidence
                    else f"linear_multi_contour_{self.layer_polarity}"
                )

            for x_index, y_index, dx_mm, dy_mm in self._iter_repetitions():
                transformed = tuple(
                    self._transform_output_point(point, dx_mm, dy_mm)
                    for point in points
                )
                transformed_holes = tuple(
                    tuple(
                        self._transform_output_point(point, dx_mm, dy_mm)
                        for point in ring
                    )
                    for ring in holes
                )
                transformed_region = CopperRegion(
                    "validation",
                    transformed,
                    self.layer,
                    holes=transformed_holes,
                )
                transformed_shape = region_shape(transformed_region)
                if (
                    transformed_shape.is_empty
                    or float(transformed_shape.area) <= 0
                    or not transformed_shape.is_valid
                ):
                    self._parse_error_or_warn(
                        path,
                        line_no,
                        line,
                        "GERBER_REGION_TRANSFORM_INVALID",
                        (
                            "image transforms produced invalid geometry for "
                            f"contour {contour_index + 1}/{contour_count}"
                        ),
                        out,
                    )
                    return

                id_parts: list[object] = [
                    path.name,
                    start_line,
                    line_no,
                    self.layer,
                    "contour",
                    contour_index,
                    contour_count,
                    coords,
                    hole_coords,
                ]
                id_parts.extend(self._image_transform_id_parts())
                if self.step_repeat is not None:
                    id_parts.extend(["sr", x_index, y_index])
                obj_id = stable_id("reg", *id_parts)
                prov = self._step_repeat_provenance(
                    end_src,
                    x_index or 0,
                    y_index or 0,
                    dx_mm,
                    dy_mm,
                )
                for source in sources:
                    prov.add_source(source)
                for evidence in arc_evidence:
                    prov.add_evidence(evidence)
                for evidence in cutin_evidence:
                    prov.add_evidence(evidence)
                prov.add_evidence(
                    Evidence(
                        "gerber_region",
                        (
                            f"{region_kind}; "
                            f"contour={contour_index + 1}/{contour_count}; "
                            f"statement_fill=union; "
                            f"vertices={len(unique)}; "
                            f"holes={len(holes)}; "
                            f"cut_ins={len(cutin_evidence)}; "
                            f"arc_commands={len(arc_evidence)}; "
                            f"source_area_mm2={float(source_shape.area):.12g}; "
                            f"output_area_mm2={float(transformed_shape.area):.12g}"
                        ),
                        1.0,
                        end_src,
                    )
                )
                region = CopperRegion(
                    obj_id,
                    transformed,
                    self.layer,
                    provenance=prov,
                    holes=transformed_holes,
                )
                out.regions.append(region)
                self.material_image_operations.append(self.layer_polarity, region)

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
        if aperture.hole_diameter is not None:
            self._fail_or_warn(
                path,
                line_no,
                line,
                "UNSUPPORTED_GERBER_APERTURE_HOLE_DRAW",
                (
                    "G02/G03 interpolation with a holed aperture is not yet "
                    "modeled safely"
                ),
                out,
            )
            self.current = nxt
            return
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

        if not isclose(self.scale_a, self.scale_b, rel_tol=0.0, abs_tol=1e-12):
            self._fail_or_warn(
                path,
                line_no,
                line,
                "UNSUPPORTED_GERBER_ANISOTROPIC_ARC_SCALE",
                (
                    "anisotropic legacy SF scaling turns circular interpolation "
                    "into non-circular geometry and is not modeled exactly"
                ),
                out,
            )
            if not self.strict:
                self._disable_image_geometry(out)
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
            output_scale = self.scale_a
            source_chord_error = _ARC_MAX_CHORD_ERROR_MM / output_scale
            segment_count = segments_for_chord_error(
                spec,
                source_chord_error,
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
        source_direction = "CW" if clockwise else "CCW"
        output_direction = self._output_arc_direction(clockwise)
        width = max(aperture.x, aperture.y) * self.aperture_scale
        if isclose(width, 0.0, rel_tol=0.0, abs_tol=0.0):
            self._record_zero_size_object(
                path,
                line_no,
                line,
                out,
                "1",
            )
            self.current = nxt
            return

        for x_index, y_index, dx_mm, dy_mm in self._iter_repetitions():
            repeated_center = self._transform_output_point(
                center, dx_mm, dy_mm
            )
            for segment_index in range(segment_count):
                start_geo = points[segment_index]
                end_geo = points[segment_index + 1]
                start = self._transform_output_point(
                    Point(start_geo.x, start_geo.y), dx_mm, dy_mm
                )
                end = self._transform_output_point(
                    Point(end_geo.x, end_geo.y), dx_mm, dy_mm
                )

                id_parts = [
                    path.name,
                    line_no,
                    self.current.x,
                    self.current.y,
                    nxt.x,
                    nxt.y,
                    center.x,
                    center.y,
                    source_direction,
                    segment_index,
                    segment_count,
                    width,
                    self.layer,
                ]
                id_parts.extend(self._image_transform_id_parts())
                id_parts.extend(self._aperture_transform_id_parts())
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
                self._add_aperture_transform_provenance(prov)
                prov.add_evidence(
                    Evidence(
                        "gerber_arc_tessellation",
                        (
                            f"quadrant_mode={self.quadrant_mode}; "
                            f"direction={output_direction}; "
                            f"source_direction={source_direction}; "
                            f"output_direction={output_direction}; "
                            f"center_mm=({repeated_center.x:.12g},"
                            f"{repeated_center.y:.12g}); "
                            f"radius_mm={radius * self.scale_a:.12g}; "
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
                    track = Track(
                        obj_id,
                        start,
                        end,
                        width,
                        self.layer,
                        provenance=prov,
                    )
                    out.tracks.append(track)
                    self.material_image_operations.append(
                        self.layer_polarity,
                        track,
                    )

        self.current = nxt

    def _composition_geometry_shape(self, geometry):
        """Return bounded polygonal geometry for the LPC material subset."""
        if isinstance(geometry, CopperRegion):
            return region_shape(geometry)
        if isinstance(geometry, PadCandidate) and geometry.shape.upper() in {"C", "R", "O"}:
            return polygonize_flash(
                geometry.center.x,
                geometry.center.y,
                geometry.size_x,
                geometry.size_y,
                geometry.shape,
                max_chord_error_mm=_ARC_MAX_CHORD_ERROR_MM,
                max_arc_segments=_MAX_ARC_SEGMENTS,
            ).geometry
        if isinstance(geometry, Track):
            return polygonize_track(
                geometry.start.x,
                geometry.start.y,
                geometry.end.x,
                geometry.end.y,
                geometry.width,
                max_chord_error_mm=_ARC_MAX_CHORD_ERROR_MM,
                max_arc_segments=_MAX_ARC_SEGMENTS,
            ).geometry
        raise TypeError(
            "LPC composition supports CopperRegion, solid C/R/O PadCandidate, "
            "and linear circular-aperture Track geometry"
        )

    def _composition_polygonization_evidence(
        self,
        geometry,
    ) -> Evidence | None:
        """Describe bounded curved-flash polygonization when a component uses it."""
        source = geometry.provenance.sources[0] if geometry.provenance.sources else None
        if isinstance(geometry, PadCandidate):
            if geometry.shape.upper() not in {"C", "O"}:
                return None
            polygonization = polygonize_flash(
                geometry.center.x,
                geometry.center.y,
                geometry.size_x,
                geometry.size_y,
                geometry.shape,
                max_chord_error_mm=_ARC_MAX_CHORD_ERROR_MM,
                max_arc_segments=_MAX_ARC_SEGMENTS,
            )
            return Evidence(
                "gerber_flash_polygonization",
                (
                    f"shape={geometry.shape.upper()}; "
                    f"method=inscribed_chords; "
                    f"curved_segments={polygonization.curved_segments}; "
                    f"max_chord_error_mm={polygonization.max_chord_error_mm:.12g}"
                ),
                1.0,
                source,
            )
        if isinstance(geometry, Track):
            polygonization = polygonize_track(
                geometry.start.x,
                geometry.start.y,
                geometry.end.x,
                geometry.end.y,
                geometry.width,
                max_chord_error_mm=_ARC_MAX_CHORD_ERROR_MM,
                max_arc_segments=_MAX_ARC_SEGMENTS,
            )
            arc_segment = any(
                evidence.kind == "gerber_arc_tessellation"
                for evidence in geometry.provenance.evidence
            )
            detail = (
                "aperture_shape=C; method=capsule_inscribed_chords; "
                f"length_mm={polygonization.length_mm:.12g}; "
                f"width_mm={geometry.width:.12g}; "
                f"curved_segments={polygonization.curved_segments}; "
                f"max_chord_error_mm={polygonization.max_chord_error_mm:.12g}"
            )
            if arc_segment:
                detail += (
                    f"; centerline_chord_error_mm={_ARC_MAX_CHORD_ERROR_MM:.12g}; "
                    f"combined_boundary_error_mm<={2 * _ARC_MAX_CHORD_ERROR_MM:.12g}"
                )
            return Evidence(
                "gerber_track_polygonization",
                detail,
                1.0,
                source,
            )
        return None

    def _composition_contribution_affects_component(
        self,
        operation,
        contribution_geometry,
        component_shape,
    ) -> bool:
        """Return whether one effective ordered contribution reaches a component."""
        if contribution_geometry.is_empty:
            return False
        if operation.polarity == "dark":
            overlap = component_shape.intersection(contribution_geometry)
            return not overlap.is_empty and float(overlap.area) > 1e-15

        boundary_overlap = component_shape.boundary.intersection(
            contribution_geometry
        )
        return (
            not boundary_overlap.is_empty
            and float(boundary_overlap.length) > 1e-12
        )

    def _layer_polarity_source_for_operation(self, operation) -> SourceRef | None:
        """Return the LP command that established polarity for one region operation."""
        source_lines = [
            source.line
            for source in operation.geometry.provenance.sources
            if source.line is not None
        ]
        if not source_lines:
            return None

        operation_line = min(source_lines)
        candidates = [
            source
            for source in self.layer_polarity_sources
            if source.line is not None and source.line <= operation_line
        ]
        if not candidates:
            return None
        return max(candidates, key=lambda source: source.line or -1)

    def _finalize_layer_polarity_image(
        self,
        path: Path,
        out: GerberLayerResult,
    ) -> None:
        """Materialize the bounded polygonal LPC image subset.

        Supported G36/G37 regions, rectangular, regular-polygon, and valid Code-4
        outline-macro D03 flashes, rectangular linear-aperture D01 sweeps, and
        solid regular-polygon D01
        sweeps are exact. Circular/obround
        D03 flashes plus
        circular/obround linear-aperture D01 sweeps use deterministic
        inscribed-chord polygonization. Curved linear sweeps have a 0.005 mm
        boundary target. Tessellated G02/G03 circular-aperture arc tracks combine the
        existing 0.005 mm centerline chord target with the 0.005 mm capsule-cap
        target for a conservative <=0.010 mm boundary-deviation budget. Outline
        segments remain fail-closed.
        """
        if not self.clear_polarity_seen:
            return

        clear_source = self.first_clear_polarity_source
        source_line = clear_source.line if clear_source is not None else None
        source_raw = clear_source.raw if clear_source is not None else "%LPC*%"

        material_track_ids = {
            operation.geometry.id
            for operation in self.material_image_operations.operations
            if isinstance(operation.geometry, Track)
        }
        unsupported_tracks = [
            track for track in out.tracks if track.id not in material_track_ids
        ]
        if unsupported_tracks or out.outline:
            self._fail_or_warn(
                path,
                source_line or 0,
                source_raw or "%LPC*%",
                "UNSUPPORTED_GERBER_CLEAR_POLARITY_NON_POLYGONAL_GEOMETRY",
                (
                    "clear Gerber layer polarity supports G36/G37 regions, "
                    "C/R/O/P D03 flashes, valid Code-4 outline-macro D03 flashes, "
                    "linear C/R/O/P D01 aperture sweeps, and circular-aperture "
                    "G02/G03 tessellation; unsupported track forms or Edge.Cuts outline "
                    "geometry remain outside the bounded polygon-composition subset"
                ),
                out,
            )
            if not self.strict:
                self._disable_image_geometry(out)
            return

        unsupported_pads = [
            pad for pad in out.pads if pad.shape.upper() not in {"C", "R", "O"}
        ]
        if unsupported_pads:
            self._fail_or_warn(
                path,
                source_line or 0,
                source_raw or "%LPC*%",
                "UNSUPPORTED_GERBER_CLEAR_POLARITY_FLASH_SHAPE",
                (
                    "clear Gerber layer polarity supports C/R/O PadCandidate flashes "
                    "plus polygon-materialized P and transformed/holed flashes "
                    "in the bounded polygon-composition subset"
                ),
                out,
            )
            if not self.strict:
                self._disable_image_geometry(out)
            return

        shape_stream = ImageCompositionStream()
        for operation in self.material_image_operations.operations:
            shape_stream.append(
                operation.polarity,
                self._composition_geometry_shape(operation.geometry),
            )

        try:
            trace = trace_polygon_operation_contributions(shape_stream.operations)
            components = canonical_polygon_components(trace.image)
        except (TypeError, ValueError) as exc:
            self._parse_error_or_warn(
                path,
                source_line or 0,
                source_raw or "%LPC*%",
                "INVALID_GERBER_LAYER_POLARITY_COMPOSITION",
                f"ordered Gerber layer-polarity composition failed: {exc}",
                out,
            )
            if not self.strict:
                self._disable_image_geometry(out)
            return

        operations = self.material_image_operations.operations
        contribution_by_sequence = {
            contribution.sequence: contribution.geometry
            for contribution in trace.contributions
        }
        dark_count = sum(operation.polarity == "dark" for operation in operations)
        clear_count = sum(operation.polarity == "clear" for operation in operations)
        output_count = len(components)
        composed_regions: list[CopperRegion] = []

        for component_index, component in enumerate(components):
            shell = tuple(Point(x, y) for x, y in component.shell)
            holes = tuple(
                tuple(Point(x, y) for x, y in ring)
                for ring in component.holes
            )
            validation_region = CopperRegion(
                "validation",
                shell,
                self.layer,
                holes=holes,
            )
            component_shape = region_shape(validation_region)
            relevant_operations = tuple(
                operation
                for operation in operations
                if self._composition_contribution_affects_component(
                    operation,
                    contribution_by_sequence[operation.sequence],
                    component_shape,
                )
            )
            relevant_signature = tuple(
                (operation.polarity, operation.geometry.id)
                for operation in relevant_operations
            )
            obj_id = stable_id(
                "regcmp",
                path.name,
                self.layer,
                relevant_signature,
                component.shell,
                component.holes,
            )
            prov = Provenance()
            relevant_polarity_sources: list[tuple[object, SourceRef]] = []
            for operation in relevant_operations:
                for source in operation.geometry.provenance.sources:
                    prov.add_source(source)
                for evidence in operation.geometry.provenance.evidence:
                    prov.add_evidence(evidence)
                polygonization_evidence = self._composition_polygonization_evidence(
                    operation.geometry
                )
                if polygonization_evidence is not None:
                    prov.add_evidence(polygonization_evidence)
                polarity_source = self._layer_polarity_source_for_operation(operation)
                if polarity_source is not None:
                    prov.add_source(polarity_source)
                    relevant_polarity_sources.append((operation, polarity_source))

            region = CopperRegion(
                obj_id,
                shell,
                self.layer,
                provenance=prov,
                holes=holes,
            )
            output_area = float(component_shape.area)
            composition_source = next(
                (
                    source
                    for operation, source in relevant_polarity_sources
                    if getattr(operation, "polarity", None) == "clear"
                ),
                relevant_polarity_sources[0][1]
                if relevant_polarity_sources
                else None,
            )
            prov.add_evidence(
                Evidence(
                    "gerber_layer_polarity_composition",
                    (
                        f"ordered_operations={len(operations)}; "
                        f"effective_operations={sum(not contribution.geometry.is_empty for contribution in trace.contributions)}; "
                        f"relevant_operations={len(relevant_operations)}; "
                        f"dark_operations={dark_count}; "
                        f"clear_operations={clear_count}; "
                        f"output_component={component_index + 1}/{output_count}; "
                        f"output_area_mm2={output_area:.12g}"
                    ),
                    1.0,
                    composition_source,
                )
            )
            composed_regions.append(region)

        out.regions[:] = composed_regions
        out.pads.clear()
        out.tracks.clear()

    def parse(self, path: str | Path) -> GerberLayerResult:
        p = Path(path)
        out = GerberLayerResult()

        text = p.read_text(encoding="utf-8-sig", errors="strict")
        for line_no, line in iter_gerber_statements(text):
            if not line or line.startswith("G04"):
                continue
            if line in {"M02*", "M00*"}:
                break

            if (
                _is_structured_numeric_statement(line)
                and _contains_non_ascii_decimal_digit(line)
            ):
                self._parse_error_or_warn(
                    p,
                    line_no,
                    line,
                    "INVALID_GERBER_NUMERIC_TOKEN",
                    "Gerber numeric syntax requires ASCII decimal digits",
                    out,
                )
                if not self.strict:
                    self._disable_image_geometry(out)
                    if self.region_state.active:
                        self._abort_region()
                continue

            if self.region_state.active:
                if line in {"G37*", "G037*"}:
                    self._end_region(p, line_no, line, out)
                    continue
                if line in {"G36*", "G036*"}:
                    self._region_fail(
                        p,
                        line_no,
                        line,
                        "GERBER_REGION_NESTED",
                        "nested G36 region start is invalid",
                        out,
                    )
                    continue
                if line in {"G01*", "G1*"}:
                    self.interpolation = "linear"
                    continue
                if line in {"G02*", "G2*"}:
                    self.interpolation = "cw_arc"
                    continue
                if line in {"G03*", "G3*"}:
                    self.interpolation = "ccw_arc"
                    continue

                op_match = _OP_SELECT.match(line)
                if op_match:
                    operation = op_match.group(1)
                    if operation == "3":
                        self._region_fail(
                            p,
                            line_no,
                            line,
                            "GERBER_REGION_FLASH_UNSUPPORTED",
                            "D03 is not allowed inside a Gerber region statement",
                            out,
                        )
                        continue
                    if operation == "2":
                        if not self._require_units(p, line_no, line, out):
                            self._abort_region()
                            continue
                        self._region_coordinate(
                            p,
                            line_no,
                            line,
                            out,
                            None,
                            None,
                            "2",
                        )
                        continue
                    self.current_operation = operation
                    continue

                arc_match = _ARC_COORD.match(line)
                if arc_match:
                    gcode, x_raw, y_raw, i_raw, j_raw, op = arc_match.groups()
                    operation = op or self.current_operation
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
                        if not self._require_units(p, line_no, line, out):
                            self._abort_region()
                            continue
                        if gcode in {"G02", "G2"}:
                            self.interpolation = "cw_arc"
                        elif gcode in {"G03", "G3"}:
                            self.interpolation = "ccw_arc"
                        self._region_arc_coordinate(
                            p,
                            line_no,
                            line,
                            out,
                            x_raw,
                            y_raw,
                            i_raw,
                            j_raw,
                            op,
                        )
                        continue

                coord_match = _COORD.match(line)
                if coord_match:
                    if not self._require_units(p, line_no, line, out):
                        self._abort_region()
                        continue
                    x_raw, y_raw, op = coord_match.groups()
                    self._region_coordinate(
                        p,
                        line_no,
                        line,
                        out,
                        x_raw,
                        y_raw,
                        op,
                    )
                    continue

                self._region_fail(
                    p,
                    line_no,
                    line,
                    "GERBER_REGION_UNSUPPORTED_STATEMENT",
                    (
                        "only D01/D02 and G01/G02/G03 contour commands are "
                        "supported inside the current region subset"
                    ),
                    out,
                )
                continue

            if line == "M01*":
                out.diagnostics.append(
                    ParseDiagnostic(
                        "info",
                        "GERBER_OPTIONAL_STOP_IGNORED",
                        "legacy M01 optional stop has no image effect",
                        str(p),
                        line_no,
                    )
                )
                continue
            if line == "G55*":
                out.diagnostics.append(
                    ParseDiagnostic(
                        "info",
                        "GERBER_PREPARE_FLASH_IGNORED",
                        "legacy G55 prepare-for-flash code has no image effect",
                        str(p),
                        line_no,
                    )
                )
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
                zs, notation, xi, xd, yi, yd = m.groups()
                self.xfmt = CoordinateFormat(int(xi), int(xd), zs)
                self.yfmt = CoordinateFormat(int(yi), int(yd), zs)
                if notation == "I":
                    self.incremental = True
                elif notation == "A":
                    self.incremental = False
                continue

            m = _MO.match(line)
            if m:
                units = "mm" if m.group(1) == "MM" else "inch"
                self._declare_units(units, p, line_no, line, out)
                continue

            # Legacy RS-274-D/early RS-274X unit commands still appear in
            # exported CAM jobs. Treat them as explicit unit declarations.
            if line in {"G70*", "G070*"}:
                self._declare_units("inch", p, line_no, line, out)
                continue
            if line in {"G71*", "G071*"}:
                self._declare_units("mm", p, line_no, line, out)
                continue

            # Legacy G90/G91 coordinate notation is modal and equivalent to
            # the absolute/incremental notation state carried by FS.
            if line in {"G90*", "G090*"}:
                self.incremental = False
                continue
            if line in {"G91*", "G091*"}:
                self.incremental = True
                continue

            if line.startswith("%AS"):
                self._handle_axis_select(line, p, line_no, out)
                continue

            if line.startswith("%IN"):
                self._handle_image_name(line, p, line_no, out)
                continue

            if line.startswith("%LN"):
                self._handle_load_name(line, p, line_no, out)
                continue

            # Deprecated MI mirrors coordinate data only. Apertures and
            # step-repeat distances are intentionally left unmirrored.
            if line.startswith("%MI"):
                self._handle_mirror_image(line, p, line_no, out)
                continue

            # Deprecated OF translates the full image in the active MO units.
            # It is applied after MI/SF and before IR, regardless of command order.
            if line.startswith("%OF"):
                self._handle_legacy_offset(line, p, line_no, out)
                continue

            # Deprecated whole-image rotation is exactly representable for the
            # four orthogonal angles allowed by the Gerber specification.
            if line.startswith("%IR"):
                self._handle_image_rotation(line, p, line_no, out)
                continue

            # Legacy SF is recognized explicitly. Identity scaling is harmless;
            # non-identity scaling remains fail-closed until coordinate scaling,
            # arc semantics, and the non-scaled aperture/SR rules are modeled.
            if line.startswith("%SF"):
                self._handle_legacy_scale_factor(line, p, line_no, out)
                continue

            # Deprecated IP is a once-only whole-image header command.
            # Positive polarity matches the parser's normal image semantics;
            # negative polarity remains fail-closed because it inverts the image plane.
            if line.startswith("%IP"):
                self._handle_image_polarity(line, p, line_no, out)
                continue

            if line.startswith("%AM"):
                self._register_aperture_macro(line, p, line_no, out)
                continue

            m = _AD_STANDARD.match(line)
            if m:
                if not self._require_units(p, line_no, line, out):
                    continue
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
                if not self._require_units(p, line_no, line, out):
                    continue
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
                if line != "%SR*%" and not self._require_units(
                    p, line_no, line, out
                ):
                    continue
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
                if not self._require_units(p, line_no, line, out):
                    continue
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

                    nxt = self._coordinate_point(x_raw, y_raw)
                    self.image_body_started = True

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

            if line in {"G36*", "G036*"}:
                self._begin_region(p, line_no, line, out)
                continue

            if line in {"G37*", "G037*"}:
                self._end_region(p, line_no, line, out)
                continue

            if line.startswith("%AB"):
                self._fail_or_warn(
                    p,
                    line_no,
                    line,
                    "UNSUPPORTED_GERBER_CONSTRUCT",
                    (
                        "Gerber aperture blocks are not implemented safely; "
                        "interpreting their body as ordinary draws/flashes would corrupt geometry"
                    ),
                    out,
                )
                if not self.strict:
                    self._disable_image_geometry(out)
                continue

            m = _COORD.match(line)
            if m:
                if not self._require_units(p, line_no, line, out):
                    continue
                x_raw, y_raw, op = m.groups()
                operation = op or self.current_operation
                if op is not None:
                    self.current_operation = op
                nxt = self._coordinate_point(x_raw, y_raw)
                self.image_body_started = True

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

                if (
                    ap.shape == "C"
                    and isclose(ap.x, 0.0, rel_tol=0.0, abs_tol=0.0)
                    and ap.hole_diameter is None
                    and operation in {"1", "3"}
                ):
                    self._record_zero_size_object(
                        p,
                        line_no,
                        line,
                        out,
                        operation,
                    )
                    self.current = nxt
                    continue

                if operation == "1":
                    if ap.shape == "AM4":
                        self._fail_or_warn(
                            p,
                            line_no,
                            line,
                            "UNSUPPORTED_GERBER_OUTLINE_MACRO_DRAW",
                            (
                                "general Code-4 outline macro apertures are supported "
                                "as exact D03 flashes only; D01 sweeps of arbitrary "
                                "outline geometry remain fail-closed"
                            ),
                            out,
                        )
                        self.current = nxt
                        continue

                    if ap.shape == "P":
                        if ap.hole_diameter is not None:
                            self._fail_or_warn(
                                p,
                                line_no,
                                line,
                                "UNSUPPORTED_GERBER_APERTURE_HOLE_DRAW",
                                (
                                    "linear D01 draw with a holed P aperture is "
                                    "not yet modeled safely"
                                ),
                                out,
                            )
                            self.current = nxt
                            continue
                        if self.layer == "Edge.Cuts":
                            self._fail_or_warn(
                                p,
                                line_no,
                                line,
                                "NON_CIRCULAR_DRAW",
                                (
                                    "P polygon Edge.Cuts draw apertures are not "
                                    "represented as centerline outline segments"
                                ),
                                out,
                            )
                            self.current = nxt
                            continue
                        if ap.polygon_vertices is None:
                            self._parse_error_or_warn(
                                p,
                                line_no,
                                line,
                                "GERBER_POLYGON_DRAW_INVALID",
                                "P aperture is missing its vertex count",
                                out,
                            )
                            self.current = nxt
                            continue

                        scaled_outer = ap.x * self.aperture_scale
                        output_rotation = (
                            self.aperture_rotation_deg + self.image_rotation_deg
                        ) % 360.0
                        for x_index, y_index, dx_mm, dy_mm in self._iter_repetitions():
                            start_point = self._transform_output_point(
                                self.current, dx_mm, dy_mm
                            )
                            end_point = self._transform_output_point(
                                nxt, dx_mm, dy_mm
                            )
                            try:
                                polygonization = polygonize_regular_polygon_track(
                                    start_point.x,
                                    start_point.y,
                                    end_point.x,
                                    end_point.y,
                                    scaled_outer,
                                    ap.polygon_vertices,
                                    base_rotation_deg=ap.polygon_rotation_deg,
                                    mirror=self.aperture_mirror,
                                    object_rotation_deg=output_rotation,
                                )
                                components = canonical_polygon_components(
                                    polygonization.geometry
                                )
                            except (TypeError, ValueError) as exc:
                                self._parse_error_or_warn(
                                    p,
                                    line_no,
                                    line,
                                    "GERBER_POLYGON_DRAW_INVALID",
                                    f"polygon linear draw materialization failed: {exc}",
                                    out,
                                )
                                continue

                            if len(components) != 1 or components[0].holes:
                                self._parse_error_or_warn(
                                    p,
                                    line_no,
                                    line,
                                    "GERBER_POLYGON_DRAW_INVALID",
                                    (
                                        "polygon linear draw did not produce one "
                                        "simply connected component"
                                    ),
                                    out,
                                )
                                continue

                            component = components[0]
                            shell = tuple(Point(x, y) for x, y in component.shell)
                            id_parts = [
                                p.name,
                                line_no,
                                "polygon_linear_sweep",
                                self.current.x,
                                self.current.y,
                                nxt.x,
                                nxt.y,
                                ap.code,
                                scaled_outer,
                                ap.polygon_vertices,
                                ap.polygon_rotation_deg,
                                self.aperture_mirror,
                                output_rotation,
                                self.layer,
                            ]
                            id_parts.extend(self._image_transform_id_parts())
                            id_parts.extend(self._aperture_transform_id_parts())
                            if self.step_repeat is not None:
                                id_parts.extend(["sr", x_index, y_index])
                            obj_id = stable_id("reg", *id_parts)
                            prov = self._step_repeat_provenance(
                                src, x_index or 0, y_index or 0, dx_mm, dy_mm
                            )
                            self._add_aperture_transform_provenance(prov)
                            prov.add_evidence(
                                Evidence(
                                    "gerber_polygon_track",
                                    (
                                        f"vertices={ap.polygon_vertices}; "
                                        f"outer_diameter_mm={scaled_outer:.12g}; "
                                        f"template_rotation_deg_ccw="
                                        f"{ap.polygon_rotation_deg:.12g}; "
                                        f"mirror={self.aperture_mirror}; "
                                        f"object_rotation_deg_ccw="
                                        f"{output_rotation:.12g}; "
                                        f"length_mm="
                                        f"{polygonization.length_mm:.12g}; "
                                        "method=convex_sweep_exact; "
                                        "approximated=false"
                                    ),
                                    1.0,
                                    src,
                                )
                            )
                            region = CopperRegion(
                                obj_id,
                                shell,
                                self.layer,
                                provenance=prov,
                            )
                            out.regions.append(region)
                            self.material_image_operations.append(
                                self.layer_polarity,
                                region,
                            )

                        self.current = nxt
                        continue

                    if ap.hole_diameter is not None:
                        self._fail_or_warn(
                            p,
                            line_no,
                            line,
                            "UNSUPPORTED_GERBER_APERTURE_HOLE_DRAW",
                            (
                                "linear D01 draw with a holed aperture is not yet "
                                "modeled safely"
                            ),
                            out,
                        )
                        self.current = nxt
                        continue
                    if ap.shape == "C":
                        width = ap.x * self.aperture_scale

                        for x_index, y_index, dx_mm, dy_mm in self._iter_repetitions():
                            start_point = self._transform_output_point(
                                self.current, dx_mm, dy_mm
                            )
                            end_point = self._transform_output_point(
                                nxt, dx_mm, dy_mm
                            )
                            id_parts = [
                                p.name,
                                line_no,
                                self.current.x,
                                self.current.y,
                                nxt.x,
                                nxt.y,
                                width,
                                self.layer,
                            ]
                            id_parts.extend(self._image_transform_id_parts())
                            id_parts.extend(self._aperture_transform_id_parts())
                            if self.step_repeat is not None:
                                id_parts.extend(["sr", x_index, y_index])
                            obj_id = stable_id("trk", *id_parts)
                            prov = self._step_repeat_provenance(
                                src, x_index or 0, y_index or 0, dx_mm, dy_mm
                            )
                            self._add_aperture_transform_provenance(prov)
                            if self.layer == "Edge.Cuts":
                                out.outline.append(
                                    OutlineSegment(obj_id, start_point, end_point, prov)
                                )
                            else:
                                track = Track(
                                    obj_id,
                                    start_point,
                                    end_point,
                                    width,
                                    self.layer,
                                    provenance=prov,
                                )
                                out.tracks.append(track)
                                self.material_image_operations.append(
                                    self.layer_polarity,
                                    track,
                                )
                    else:
                        if self.layer == "Edge.Cuts":
                            self._fail_or_warn(
                                p,
                                line_no,
                                line,
                                "NON_CIRCULAR_DRAW",
                                (
                                    "non-circular Edge.Cuts draw apertures are not "
                                    "represented as centerline outline segments"
                                ),
                                out,
                            )
                            self.current = nxt
                            continue

                        size_x = ap.x * self.aperture_scale
                        size_y = ap.y * self.aperture_scale
                        output_aperture_rotation = (
                            self._effective_rectangular_aperture_rotation(ap)
                            if ap.shape in {"R", "O"}
                            else (
                                self.aperture_rotation_deg + self.image_rotation_deg
                            ) % 360.0
                        )

                        for x_index, y_index, dx_mm, dy_mm in self._iter_repetitions():
                            start_point = self._transform_output_point(
                                self.current, dx_mm, dy_mm
                            )
                            end_point = self._transform_output_point(
                                nxt, dx_mm, dy_mm
                            )
                            try:
                                polygonization = polygonize_aperture_track(
                                    start_point.x,
                                    start_point.y,
                                    end_point.x,
                                    end_point.y,
                                    size_x,
                                    size_y,
                                    ap.shape,
                                    rotation_deg=output_aperture_rotation,
                                    max_chord_error_mm=_ARC_MAX_CHORD_ERROR_MM,
                                    max_arc_segments=_MAX_ARC_SEGMENTS,
                                )
                                components = canonical_polygon_components(
                                    polygonization.geometry
                                )
                            except (TypeError, ValueError) as exc:
                                self._parse_error_or_warn(
                                    p,
                                    line_no,
                                    line,
                                    "GERBER_NONCIRCULAR_DRAW_INVALID",
                                    f"non-circular linear draw polygonization failed: {exc}",
                                    out,
                                )
                                continue

                            if len(components) != 1 or components[0].holes:
                                self._parse_error_or_warn(
                                    p,
                                    line_no,
                                    line,
                                    "GERBER_NONCIRCULAR_DRAW_INVALID",
                                    (
                                        "non-circular linear draw sweep did not "
                                        "produce one simply connected polygon"
                                    ),
                                    out,
                                )
                                continue

                            component = components[0]
                            shell = tuple(Point(x, y) for x, y in component.shell)
                            id_parts = [
                                p.name,
                                line_no,
                                "linear_aperture_sweep",
                                self.current.x,
                                self.current.y,
                                nxt.x,
                                nxt.y,
                                ap.code,
                                ap.shape,
                                size_x,
                                size_y,
                                output_aperture_rotation,
                                self.layer,
                            ]
                            id_parts.extend(self._image_transform_id_parts())
                            id_parts.extend(self._aperture_transform_id_parts())
                            if self.step_repeat is not None:
                                id_parts.extend(["sr", x_index, y_index])
                            obj_id = stable_id("reg", *id_parts)
                            prov = self._step_repeat_provenance(
                                src, x_index or 0, y_index or 0, dx_mm, dy_mm
                            )
                            self._add_aperture_transform_provenance(prov)
                            method = (
                                "convex_sweep_exact"
                                if not polygonization.approximated
                                else "convex_sweep_inscribed_chords"
                            )
                            prov.add_evidence(
                                Evidence(
                                    "gerber_track_polygonization",
                                    (
                                        f"aperture_shape={ap.shape}; "
                                        f"method={method}; "
                                        f"length_mm={polygonization.length_mm:.12g}; "
                                        f"size_x_mm={size_x:.12g}; "
                                        f"size_y_mm={size_y:.12g}; "
                                        f"rotation_deg_ccw="
                                        f"{output_aperture_rotation:.12g}; "
                                        f"curved_segments={polygonization.curved_segments}; "
                                        f"max_chord_error_mm="
                                        f"{polygonization.max_chord_error_mm:.12g}; "
                                        f"approximated={str(polygonization.approximated).lower()}"
                                    ),
                                    1.0,
                                    src,
                                )
                            )
                            region = CopperRegion(
                                obj_id,
                                shell,
                                self.layer,
                                provenance=prov,
                            )
                            out.regions.append(region)
                            self.material_image_operations.append(
                                self.layer_polarity,
                                region,
                            )

                elif operation == "3":
                    if ap.shape == "AM4":
                        if self.layer == "Edge.Cuts":
                            self._fail_or_warn(
                                p,
                                line_no,
                                line,
                                "UNSUPPORTED_GERBER_OUTLINE_MACRO_FLASH_EDGE",
                                (
                                    "general Code-4 outline macro D03 flashes are "
                                    "supported only on material layers"
                                ),
                                out,
                            )
                            self.current = nxt
                            continue
                        if not ap.outline_vertices:
                            self._parse_error_or_warn(
                                p,
                                line_no,
                                line,
                                "GERBER_OUTLINE_MACRO_FLASH_INVALID",
                                "Code-4 outline aperture is missing its vertices",
                                out,
                            )
                            self.current = nxt
                            continue

                        output_rotation = (
                            self.aperture_rotation_deg + self.image_rotation_deg
                        ) % 360.0
                        for x_index, y_index, dx_mm, dy_mm in self._iter_repetitions():
                            center = self._transform_output_point(
                                nxt, dx_mm, dy_mm
                            )
                            try:
                                flash_points = self._outline_macro_flash_points(
                                    ap, center
                                )
                                geometry = Polygon(
                                    [(point.x, point.y) for point in flash_points]
                                )
                                components = canonical_polygon_components(geometry)
                            except (TypeError, ValueError) as exc:
                                self._parse_error_or_warn(
                                    p,
                                    line_no,
                                    line,
                                    "GERBER_OUTLINE_MACRO_FLASH_INVALID",
                                    (
                                        "Code-4 outline flash materialization "
                                        f"failed: {exc}"
                                    ),
                                    out,
                                )
                                continue

                            if len(components) != 1 or components[0].holes:
                                self._parse_error_or_warn(
                                    p,
                                    line_no,
                                    line,
                                    "GERBER_OUTLINE_MACRO_FLASH_INVALID",
                                    (
                                        "Code-4 outline flash did not produce one "
                                        "simply connected polygon"
                                    ),
                                    out,
                                )
                                continue

                            component = components[0]
                            shell = tuple(Point(x, y) for x, y in component.shell)
                            id_parts = [
                                p.name,
                                line_no,
                                "outline_macro_flash",
                                nxt.x,
                                nxt.y,
                                ap.code,
                                len(ap.outline_vertices),
                                ap.outline_rotation_deg,
                                self.aperture_mirror,
                                self.aperture_scale,
                                output_rotation,
                                self.layer,
                            ]
                            id_parts.extend(
                                coordinate
                                for vertex in ap.outline_vertices
                                for coordinate in vertex
                            )
                            id_parts.extend(self._image_transform_id_parts())
                            id_parts.extend(self._aperture_transform_id_parts())
                            if self.step_repeat is not None:
                                id_parts.extend(["sr", x_index, y_index])
                            obj_id = stable_id("reg", *id_parts)
                            prov = self._step_repeat_provenance(
                                src, x_index or 0, y_index or 0, dx_mm, dy_mm
                            )
                            self._add_aperture_transform_provenance(prov)
                            prov.add_evidence(
                                Evidence(
                                    "gerber_outline_macro_flash",
                                    (
                                        f"vertices={len(ap.outline_vertices)}; "
                                        f"primitive_rotation_deg_ccw="
                                        f"{ap.outline_rotation_deg:.12g}; "
                                        f"mirror={self.aperture_mirror}; "
                                        f"aperture_scale={self.aperture_scale:.12g}; "
                                        f"object_rotation_deg_ccw="
                                        f"{output_rotation:.12g}; "
                                        "method=exact_linear_outline; "
                                        "approximated=false"
                                    ),
                                    1.0,
                                    src,
                                )
                            )
                            region = CopperRegion(
                                obj_id,
                                shell,
                                self.layer,
                                provenance=prov,
                            )
                            out.regions.append(region)
                            self.material_image_operations.append(
                                self.layer_polarity,
                                region,
                            )

                        self.current = nxt
                        continue

                    if ap.shape == "P":
                        if self.layer == "Edge.Cuts":
                            self._fail_or_warn(
                                p,
                                line_no,
                                line,
                                "UNSUPPORTED_GERBER_POLYGON_FLASH_EDGE",
                                (
                                    "standard P D03 flashes are supported only "
                                    "on material layers"
                                ),
                                out,
                            )
                            self.current = nxt
                            continue
                        if ap.polygon_vertices is None:
                            self._parse_error_or_warn(
                                p,
                                line_no,
                                line,
                                "GERBER_POLYGON_FLASH_INVALID",
                                "P aperture is missing its vertex count",
                                out,
                            )
                            self.current = nxt
                            continue

                        scaled_outer = ap.x * self.aperture_scale
                        scaled_hole = (
                            None
                            if ap.hole_diameter is None
                            else ap.hole_diameter * self.aperture_scale
                        )
                        output_rotation = (
                            self.aperture_rotation_deg + self.image_rotation_deg
                        ) % 360.0

                        for x_index, y_index, dx_mm, dy_mm in self._iter_repetitions():
                            center = self._transform_output_point(
                                nxt, dx_mm, dy_mm
                            )
                            try:
                                polygonization = polygonize_regular_polygon_flash(
                                    center.x,
                                    center.y,
                                    scaled_outer,
                                    ap.polygon_vertices,
                                    base_rotation_deg=ap.polygon_rotation_deg,
                                    mirror=self.aperture_mirror,
                                    object_rotation_deg=output_rotation,
                                    hole_diameter=scaled_hole,
                                    max_chord_error_mm=_ARC_MAX_CHORD_ERROR_MM,
                                    max_arc_segments=_MAX_ARC_SEGMENTS,
                                )
                                components = canonical_polygon_components(
                                    polygonization.geometry
                                )
                            except (TypeError, ValueError) as exc:
                                self._parse_error_or_warn(
                                    p,
                                    line_no,
                                    line,
                                    "GERBER_POLYGON_FLASH_INVALID",
                                    f"polygon flash materialization failed: {exc}",
                                    out,
                                )
                                continue

                            expected_holes = 1 if scaled_hole is not None else 0
                            if (
                                len(components) != 1
                                or len(components[0].holes) != expected_holes
                            ):
                                self._parse_error_or_warn(
                                    p,
                                    line_no,
                                    line,
                                    "GERBER_POLYGON_FLASH_INVALID",
                                    (
                                        "polygon flash did not produce one "
                                        "connected component with the expected "
                                        "hole topology"
                                    ),
                                    out,
                                )
                                continue

                            component = components[0]
                            shell = tuple(Point(x, y) for x, y in component.shell)
                            holes = tuple(
                                tuple(Point(x, y) for x, y in ring)
                                for ring in component.holes
                            )
                            id_parts = [
                                p.name,
                                line_no,
                                "polygon_flash",
                                nxt.x,
                                nxt.y,
                                ap.code,
                                scaled_outer,
                                ap.polygon_vertices,
                                ap.polygon_rotation_deg,
                                self.aperture_mirror,
                                output_rotation,
                                scaled_hole,
                                self.layer,
                            ]
                            id_parts.extend(self._image_transform_id_parts())
                            id_parts.extend(self._aperture_transform_id_parts())
                            if self.step_repeat is not None:
                                id_parts.extend(["sr", x_index, y_index])
                            obj_id = stable_id("reg", *id_parts)
                            prov = self._step_repeat_provenance(
                                src, x_index or 0, y_index or 0, dx_mm, dy_mm
                            )
                            self._add_aperture_transform_provenance(prov)
                            prov.add_evidence(
                                Evidence(
                                    "gerber_polygon_flash",
                                    (
                                        f"vertices={ap.polygon_vertices}; "
                                        f"outer_diameter_mm={scaled_outer:.12g}; "
                                        f"template_rotation_deg_ccw="
                                        f"{ap.polygon_rotation_deg:.12g}; "
                                        f"mirror={self.aperture_mirror}; "
                                        f"object_rotation_deg_ccw="
                                        f"{output_rotation:.12g}; "
                                        f"hole_diameter_mm="
                                        f"{'none' if scaled_hole is None else format(scaled_hole, '.12g')}; "
                                        f"hole_curved_segments="
                                        f"{polygonization.hole_curved_segments}; "
                                        f"max_chord_error_mm="
                                        f"{polygonization.max_chord_error_mm:.12g}; "
                                        f"approximated="
                                        f"{str(polygonization.approximated).lower()}"
                                    ),
                                    1.0,
                                    src,
                                )
                            )
                            region = CopperRegion(
                                obj_id,
                                shell,
                                self.layer,
                                provenance=prov,
                                holes=holes,
                            )
                            out.regions.append(region)
                            self.material_image_operations.append(
                                self.layer_polarity,
                                region,
                            )

                        self.current = nxt
                        continue

                    if ap.hole_diameter is not None:
                        if self.layer == "Edge.Cuts":
                            self._fail_or_warn(
                                p,
                                line_no,
                                line,
                                "UNSUPPORTED_GERBER_APERTURE_HOLE_EDGE",
                                (
                                    "holed D03 flashes are supported only on "
                                    "material layers"
                                ),
                                out,
                            )
                            self.current = nxt
                            continue

                        scaled_x = ap.x * self.aperture_scale
                        scaled_y = ap.y * self.aperture_scale
                        scaled_hole = ap.hole_diameter * self.aperture_scale
                        output_aperture_rotation = (
                            self._effective_rectangular_aperture_rotation(ap)
                            if ap.shape in {"R", "O"}
                            else (self.aperture_rotation_deg + self.image_rotation_deg) % 360.0
                        )

                        for x_index, y_index, dx_mm, dy_mm in self._iter_repetitions():
                            center = self._transform_output_point(
                                nxt, dx_mm, dy_mm
                            )
                            try:
                                polygonization = polygonize_holed_flash(
                                    center.x,
                                    center.y,
                                    scaled_x,
                                    scaled_y,
                                    ap.shape,
                                    scaled_hole,
                                    rotation_deg=output_aperture_rotation,
                                    max_chord_error_mm=_ARC_MAX_CHORD_ERROR_MM,
                                    max_arc_segments=_MAX_ARC_SEGMENTS,
                                )
                                components = canonical_polygon_components(
                                    polygonization.geometry
                                )
                            except (TypeError, ValueError) as exc:
                                self._parse_error_or_warn(
                                    p,
                                    line_no,
                                    line,
                                    "GERBER_HOLED_FLASH_INVALID",
                                    f"holed flash polygonization failed: {exc}",
                                    out,
                                )
                                continue

                            if len(components) != 1 or len(components[0].holes) != 1:
                                self._parse_error_or_warn(
                                    p,
                                    line_no,
                                    line,
                                    "GERBER_HOLED_FLASH_INVALID",
                                    (
                                        "holed flash did not produce one connected "
                                        "polygon with one centered hole"
                                    ),
                                    out,
                                )
                                continue

                            component = components[0]
                            shell = tuple(Point(x, y) for x, y in component.shell)
                            holes = tuple(
                                tuple(Point(x, y) for x, y in ring)
                                for ring in component.holes
                            )
                            id_parts = [
                                p.name,
                                line_no,
                                "holed_flash",
                                nxt.x,
                                nxt.y,
                                ap.code,
                                ap.shape,
                                scaled_x,
                                scaled_y,
                                scaled_hole,
                                output_aperture_rotation,
                                self.layer,
                            ]
                            id_parts.extend(self._image_transform_id_parts())
                            id_parts.extend(self._aperture_transform_id_parts())
                            if self.step_repeat is not None:
                                id_parts.extend(["sr", x_index, y_index])
                            obj_id = stable_id("reg", *id_parts)
                            prov = self._step_repeat_provenance(
                                src, x_index or 0, y_index or 0, dx_mm, dy_mm
                            )
                            self._add_aperture_transform_provenance(prov)
                            prov.add_evidence(
                                Evidence(
                                    "gerber_aperture_hole",
                                    (
                                        f"outer_shape={ap.shape}; "
                                        f"size_x_mm={scaled_x:.12g}; "
                                        f"size_y_mm={scaled_y:.12g}; "
                                        f"hole_diameter_mm={scaled_hole:.12g}; "
                                        f"rotation_deg_ccw="
                                        f"{output_aperture_rotation:.12g}; "
                                        "hole_semantics=transparent; "
                                        f"outer_curved_segments="
                                        f"{polygonization.outer_curved_segments}; "
                                        f"hole_curved_segments="
                                        f"{polygonization.hole_curved_segments}; "
                                        f"max_chord_error_mm="
                                        f"{polygonization.max_chord_error_mm:.12g}; "
                                        f"approximated="
                                        f"{str(polygonization.approximated).lower()}"
                                    ),
                                    1.0,
                                    src,
                                )
                            )
                            region = CopperRegion(
                                obj_id,
                                shell,
                                self.layer,
                                provenance=prov,
                                holes=holes,
                            )
                            out.regions.append(region)
                            self.material_image_operations.append(
                                self.layer_polarity,
                                region,
                            )

                        self.current = nxt
                        continue

                    scaled_x = ap.x * self.aperture_scale
                    scaled_y = ap.y * self.aperture_scale
                    local_aperture_rotation = (
                        0.0
                        if ap.shape == "C"
                        else self._effective_rectangular_aperture_rotation(
                            ap,
                            include_image_rotation=False,
                        )
                    )
                    orthogonal_size = (
                        (scaled_x, scaled_y)
                        if ap.shape == "C"
                        else self._orthogonal_rectangle_size(
                            scaled_x,
                            scaled_y,
                            local_aperture_rotation,
                        )
                    )

                    if orthogonal_size is not None:
                        size_x, size_y = self._rotate_image_size(*orthogonal_size)
                        for x_index, y_index, dx_mm, dy_mm in self._iter_repetitions():
                            center = self._transform_output_point(
                                nxt, dx_mm, dy_mm
                            )
                            id_parts = [
                                p.name,
                                line_no,
                                nxt.x,
                                nxt.y,
                                ap.code,
                                ap.base_rotation_deg,
                                local_aperture_rotation,
                                self.layer,
                            ]
                            id_parts.extend(self._image_transform_id_parts())
                            id_parts.extend(self._aperture_transform_id_parts())
                            if self.step_repeat is not None:
                                id_parts.extend(["sr", x_index, y_index])
                            obj_id = stable_id("pad", *id_parts)
                            prov = self._step_repeat_provenance(
                                src, x_index or 0, y_index or 0, dx_mm, dy_mm
                            )
                            self._add_aperture_transform_provenance(prov)
                            pad = PadCandidate(
                                obj_id,
                                center,
                                size_x,
                                size_y,
                                ap.shape,
                                self.layer,
                                provenance=prov,
                            )
                            out.pads.append(pad)
                            self.material_image_operations.append(
                                self.layer_polarity,
                                pad,
                            )
                    else:
                        if self.layer == "Edge.Cuts":
                            self._fail_or_warn(
                                p,
                                line_no,
                                line,
                                "UNSUPPORTED_GERBER_APERTURE_TRANSFORM",
                                (
                                    "non-orthogonal rectangular/obround D03 flashes "
                                    "are supported only on material layers"
                                ),
                                out,
                            )
                            self.current = nxt
                            continue

                        output_aperture_rotation = (
                            self._effective_rectangular_aperture_rotation(ap)
                        )
                        for x_index, y_index, dx_mm, dy_mm in self._iter_repetitions():
                            center = self._transform_output_point(
                                nxt, dx_mm, dy_mm
                            )
                            try:
                                polygonization = polygonize_rotated_flash(
                                    center.x,
                                    center.y,
                                    scaled_x,
                                    scaled_y,
                                    ap.shape,
                                    rotation_deg=output_aperture_rotation,
                                    max_chord_error_mm=_ARC_MAX_CHORD_ERROR_MM,
                                    max_arc_segments=_MAX_ARC_SEGMENTS,
                                )
                                components = canonical_polygon_components(
                                    polygonization.geometry
                                )
                            except (TypeError, ValueError) as exc:
                                self._parse_error_or_warn(
                                    p,
                                    line_no,
                                    line,
                                    "GERBER_ROTATED_FLASH_INVALID",
                                    f"rotated flash polygonization failed: {exc}",
                                    out,
                                )
                                continue

                            if len(components) != 1 or components[0].holes:
                                self._parse_error_or_warn(
                                    p,
                                    line_no,
                                    line,
                                    "GERBER_ROTATED_FLASH_INVALID",
                                    (
                                        "rotated flash did not produce one simply "
                                        "connected polygon"
                                    ),
                                    out,
                                )
                                continue

                            component = components[0]
                            shell = tuple(Point(x, y) for x, y in component.shell)
                            id_parts = [
                                p.name,
                                line_no,
                                "rotated_flash",
                                nxt.x,
                                nxt.y,
                                ap.code,
                                ap.shape,
                                scaled_x,
                                scaled_y,
                                output_aperture_rotation,
                                self.layer,
                            ]
                            id_parts.extend(self._image_transform_id_parts())
                            id_parts.extend(self._aperture_transform_id_parts())
                            if self.step_repeat is not None:
                                id_parts.extend(["sr", x_index, y_index])
                            obj_id = stable_id("reg", *id_parts)
                            prov = self._step_repeat_provenance(
                                src, x_index or 0, y_index or 0, dx_mm, dy_mm
                            )
                            self._add_aperture_transform_provenance(prov)
                            method = (
                                "rotated_polygon_exact"
                                if not polygonization.approximated
                                else "rotated_inscribed_chords"
                            )
                            prov.add_evidence(
                                Evidence(
                                    "gerber_flash_polygonization",
                                    (
                                        f"shape={ap.shape}; "
                                        f"method={method}; "
                                        f"size_x_mm={scaled_x:.12g}; "
                                        f"size_y_mm={scaled_y:.12g}; "
                                        f"rotation_deg_ccw="
                                        f"{output_aperture_rotation:.12g}; "
                                        f"curved_segments="
                                        f"{polygonization.curved_segments}; "
                                        f"max_chord_error_mm="
                                        f"{polygonization.max_chord_error_mm:.12g}; "
                                        f"approximated="
                                        f"{str(polygonization.approximated).lower()}"
                                    ),
                                    1.0,
                                    src,
                                )
                            )
                            region = CopperRegion(
                                obj_id,
                                shell,
                                self.layer,
                                provenance=prov,
                            )
                            out.regions.append(region)
                            self.material_image_operations.append(
                                self.layer_polarity,
                                region,
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

        if self.region_state.active:
            if self.strict:
                raise ParseError(
                    f"{p}: unterminated G36 region at end of file"
                )
            out.diagnostics.append(
                ParseDiagnostic(
                    "warning",
                    "GERBER_REGION_UNTERMINATED",
                    "unterminated G36 region at end of file",
                    str(p),
                    self.region_start_line,
                )
            )
            self._abort_region()

        if self.clear_polarity_seen and self.image_geometry_enabled:
            self._finalize_layer_polarity_image(p, out)

        return out
