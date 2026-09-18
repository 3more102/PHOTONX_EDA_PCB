from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path

from .input_package import prepare_input
from .parsers import ExcellonParser, GerberRS274XParser, discover_manufacturing_files


@dataclass
class FilePreflight:
    path: str
    kind: str
    layer: str | None
    format_confidence: float
    detection_reasons: tuple[str, ...]
    status: str
    diagnostics: list[dict] = field(default_factory=list)
    strict_blockers: list[str] = field(default_factory=list)
    error: str | None = None


@dataclass
class InputPreflight:
    source: str
    input_kind: str
    files: list[FilePreflight] = field(default_factory=list)

    @property
    def discovered_files(self) -> int:
        return len(self.files)

    @property
    def strict_blockers(self) -> list[str]:
        out: list[str] = []
        for item in self.files:
            out.extend(f"{item.path}: {code}" for code in item.strict_blockers)
        return out

    @property
    def ready_for_strict_reconstruction(self) -> bool:
        return bool(self.files) and not self.strict_blockers and all(
            item.status != "failed" for item in self.files
        )

    def to_dict(self) -> dict:
        data = asdict(self)
        data["discovered_files"] = self.discovered_files
        data["strict_blockers"] = self.strict_blockers
        data["ready_for_strict_reconstruction"] = self.ready_for_strict_reconstruction
        return data


def _diag_to_dict(diag) -> dict:
    return {
        "severity": getattr(diag, "severity", "unknown"),
        "code": getattr(diag, "code", "UNKNOWN"),
        "message": getattr(diag, "message", ""),
        "path": getattr(diag, "path", None),
        "line": getattr(diag, "line", None),
    }


def _is_strict_blocker(code: str) -> bool:
    code = str(code).upper()
    return (
        code.startswith("UNSUPPORTED_")
        or code.startswith("UNKNOWN_")
        or code.startswith("INVALID_")
        or code.startswith("GERBER_ARC_") and code.endswith("_UNSUPPORTED")
        or code in {
            "NON_CIRCULAR_DRAW",
            "GERBER_STEP_REPEAT_LIMIT",
            "GERBER_INCREMENTAL_COORDINATES_UNSUPPORTED",
            "MALFORMED_EXCELLON_ROUTE",
            "EXCELLON_ROUTE_STATE",
            "EXCELLON_ROUTE_EMPTY",
            "EXCELLON_ROUTE_UNTERMINATED",
            "EXCELLON_UNITS_UNDECLARED",
        }
    )


def _scan_file(item) -> FilePreflight:
    diagnostics = []
    blockers: list[str] = []

    try:
        if item.kind == "drill":
            parsed = ExcellonParser(strict=False).parse(item.path)
        else:
            parsed = GerberRS274XParser(item.layer or "F.Cu", strict=False).parse(
                item.path
            )

        diagnostics = [_diag_to_dict(d) for d in parsed.diagnostics]
        blockers = sorted(
            {d["code"] for d in diagnostics if _is_strict_blocker(d["code"])}
        )

        if item.kind == "gerber" and item.layer is None:
            diagnostics.append(
                {
                    "severity": "warning",
                    "code": "UNKNOWN_LAYER",
                    "message": (
                        "Gerber syntax was detected, but the PCB layer could not "
                        "be inferred from X2 attributes or the filename."
                    ),
                    "path": str(item.path),
                    "line": None,
                }
            )
            blockers.append("UNKNOWN_LAYER")

        blockers = sorted(set(blockers))
        status = "supported" if not diagnostics else "partial"
        return FilePreflight(
            path=str(item.path),
            kind=item.kind,
            layer=item.layer,
            format_confidence=item.format_confidence,
            detection_reasons=item.detection_reasons,
            status=status,
            diagnostics=diagnostics,
            strict_blockers=blockers,
        )
    except Exception as exc:
        return FilePreflight(
            path=str(item.path),
            kind=item.kind,
            layer=item.layer,
            format_confidence=item.format_confidence,
            detection_reasons=item.detection_reasons,
            status="failed",
            diagnostics=diagnostics,
            strict_blockers=["PARSER_FAILURE"],
            error=f"{type(exc).__name__}: {exc}",
        )


def preflight(source: str | Path) -> InputPreflight:
    """Inspect a manufacturing package before reconstruction.

    This intentionally uses the production parsers in permissive mode. A report
    therefore reflects the syntax the current PHOTONX parser path can actually
    consume rather than only filename heuristics.
    """

    with prepare_input(source) as prepared:
        items = discover_manufacturing_files(prepared.root)
        return InputPreflight(
            source=str(prepared.original),
            input_kind=prepared.kind,
            files=[_scan_file(item) for item in items],
        )
