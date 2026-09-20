from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from ..format_detection import detect_format
from ..io.walk import DEFAULT_MAX_RECURSIVE_ENTRIES, bounded_regular_files
from .layer_map import (
    infer_layer,
    x2_file_function_declarations,
    x2_file_function_fields,
)


_GERBER_SUFFIXES = {
    ".gbr", ".ger", ".pho", ".art",
    ".gtl", ".gbl", ".gts", ".gbs", ".gto", ".gbo", ".gtp", ".gbp",
    ".gm1", ".gm2", ".gko", ".gml", ".cmp", ".sol",
}
_DRILL_SUFFIXES = {".drl", ".xln", ".xnc", ".exc", ".tap", ".drd"}


@dataclass(frozen=True)
class ManufacturingFile:
    path: Path
    kind: str
    layer: str | None = None
    format_confidence: float = 0.0
    detection_reasons: tuple[str, ...] = ()
    plating_hint: str | None = None
    x2_file_function: tuple[str, ...] = ()
    x2_file_function_conflict: bool = False


def _candidate_files(source: Path, *, max_entries: int):
    if source.is_file():
        # An explicitly selected file is intentional, even when the path itself
        # is a symlink. Recursive directory discovery is the trust boundary.
        yield source
        return
    if source.is_dir():
        yield from sorted(
            bounded_regular_files(source, max_entries=max_entries),
            key=lambda p: p.as_posix().lower(),
        )
        return
    raise FileNotFoundError(source)


def _sniff_text(path: Path, limit: int = 256 * 1024) -> str:
    """Read only the bounded prefix needed for format/layer detection."""
    try:
        with path.open("rb") as stream:
            raw = stream.read(limit)
        if b"\x00" in raw[:4096]:
            return ""
        return raw.decode("utf-8-sig", errors="ignore")
    except OSError:
        return ""


def infer_drill_plating_hint(filename: str) -> str | None:
    """Infer explicit PTH/NPTH intent from a manufacturing filename.

    This is deliberately conservative: only standalone/common plating tokens
    are accepted. Ambiguous drill filenames keep plating unresolved.
    """
    stem = Path(filename).stem.lower()
    tokens = tuple(
        token for token in re.split(r"[^a-z0-9]+", stem) if token
    )
    compact = "".join(tokens)

    if (
        "npth" in tokens
        or "nonplated" in compact
        or "unplated" in tokens
    ):
        return "non-plated"

    if "pth" in tokens or "plated" in tokens:
        return "plated"

    return None


def discover_manufacturing_files(
    source: str | Path,
    *,
    max_entries: int = DEFAULT_MAX_RECURSIVE_ENTRIES,
) -> list[ManufacturingFile]:
    """Discover Gerber/Excellon files recursively using names and content."""
    root = Path(source)
    result: list[ManufacturingFile] = []

    for p in _candidate_files(root, max_entries=max_entries):
        text = _sniff_text(p)
        guess = detect_format(p.name, text)
        suffix = p.suffix.lower()
        lower_name = p.name.lower()
        x2_declarations = x2_file_function_declarations(text)
        x2_file_function_conflict = len(x2_declarations) > 1
        x2_file_function = x2_file_function_fields(text) or ()

        is_drill = (
            guess.format == "excellon"
            or suffix in _DRILL_SUFFIXES
            or "drill" in lower_name
        )
        if is_drill:
            reasons = guess.reasons or (
                ("extension",) if suffix in _DRILL_SUFFIXES else ("filename",)
            )
            confidence = guess.confidence or (
                0.45 if suffix in _DRILL_SUFFIXES else 0.30
            )
            result.append(
                ManufacturingFile(
                    p,
                    "drill",
                    None,
                    confidence,
                    tuple(reasons),
                    infer_drill_plating_hint(p.name),
                    x2_file_function,
                    x2_file_function_conflict,
                )
            )
            continue

        layer = None if x2_file_function_conflict else infer_layer(p, text)
        is_gerber = (
            guess.format == "gerber"
            or suffix in _GERBER_SUFFIXES
            or layer is not None
        )
        if is_gerber:
            reasons = guess.reasons or (
                ("extension",) if suffix in _GERBER_SUFFIXES else ("layer_name",)
            )
            confidence = guess.confidence or (
                0.45 if suffix in _GERBER_SUFFIXES else 0.30
            )
            result.append(
                ManufacturingFile(
                    p,
                    "gerber",
                    layer,
                    confidence,
                    tuple(reasons),
                    None,
                    x2_file_function,
                    x2_file_function_conflict,
                )
            )

    return result
