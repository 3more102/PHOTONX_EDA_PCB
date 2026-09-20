from __future__ import annotations

from pathlib import Path
import re


_SUFFIXES = {
    ".gtl": "F.Cu",
    ".gbl": "B.Cu",
    ".gts": "F.Mask",
    ".gbs": "B.Mask",
    ".gto": "F.SilkS",
    ".gbo": "B.SilkS",
    ".gtp": "F.Paste",
    ".gbp": "B.Paste",
    ".gm1": "Edge.Cuts",
    ".gm2": "Edge.Cuts",
    ".gko": "Edge.Cuts",
    ".gml": "Edge.Cuts",
    ".cmp": "F.Cu",
    ".sol": "B.Cu",
    ".plc": "F.SilkS",
    ".pls": "B.SilkS",
    ".stc": "F.Mask",
    ".sts": "B.Mask",
    ".smt": "F.Paste",
    ".smb": "B.Paste",
    ".dim": "Edge.Cuts",
}

_FILE_FUNCTION = re.compile(
    r"%TF\.FileFunction,(?P<value>[^*%]+)\*%",
    re.IGNORECASE,
)


def x2_file_function_declarations(text: str) -> tuple[tuple[str, ...], ...]:
    """Return every normalized X2 FileFunction declaration in source order."""

    declarations = []
    for match in _FILE_FUNCTION.finditer(text or ""):
        parts = tuple(
            part.strip()
            for part in match.group("value").split(",")
            if part.strip()
        )
        if parts:
            declarations.append(parts)
    return tuple(declarations)


def x2_file_function_fields(text: str) -> tuple[str, ...] | None:
    """Return FileFunction fields only when the immutable attribute is unique."""

    declarations = x2_file_function_declarations(text)
    if len(declarations) != 1:
        return None
    return declarations[0]


def _x2_file_function_layer(text: str) -> str | None:
    parts = x2_file_function_fields(text)
    if not parts:
        return None

    function = parts[0].lower()
    tokens = [p.lower() for p in parts[1:]]

    side = None
    if any(t in {"top", "front"} for t in tokens):
        side = "top"
    elif any(t in {"bot", "bottom", "back"} for t in tokens):
        side = "bottom"

    if function == "copper":
        if side == "top":
            return "F.Cu"
        if side == "bottom":
            return "B.Cu"

        layer_number = None
        for token in tokens:
            m = re.fullmatch(r"l(\d+)", token)
            if m:
                layer_number = int(m.group(1))
                break
        if layer_number == 1:
            return "F.Cu"
        if layer_number and layer_number > 1:
            return f"In{layer_number - 1}.Cu"
        return None

    if function in {"soldermask", "solder_mask"}:
        return "F.Mask" if side == "top" else ("B.Mask" if side == "bottom" else None)
    if function in {"legend", "silkscreen"}:
        return "F.SilkS" if side == "top" else ("B.SilkS" if side == "bottom" else None)
    if function == "paste":
        return "F.Paste" if side == "top" else ("B.Paste" if side == "bottom" else None)
    if function in {"profile", "outline"}:
        return "Edge.Cuts"

    return None


def _filename_layer(path: Path) -> str | None:
    suffix = path.suffix.lower()
    if suffix in _SUFFIXES:
        return _SUFFIXES[suffix]

    # Common Protel/Altium inner-layer Gerber extensions: .G1, .G2, ...
    inner = re.fullmatch(r"\.g(\d+)", suffix)
    if inner:
        index = int(inner.group(1))
        if index >= 1:
            return f"In{index}.Cu"

    # Internal-plane variants are still copper layers for geometry purposes.
    plane = re.fullmatch(r"\.gp(\d+)", suffix)
    if plane:
        index = int(plane.group(1))
        if index >= 1:
            return f"In{index}.Cu"

    name = path.name.lower()
    normalized = re.sub(r"[^a-z0-9]+", "_", name)

    if any(k in normalized for k in ("outline", "edge_cuts", "board_edge", "profile")):
        return "Edge.Cuts"

    if any(k in normalized for k in ("f_cu", "top_copper", "copper_top", "front_copper")):
        return "F.Cu"
    if any(k in normalized for k in ("b_cu", "bottom_copper", "copper_bottom", "back_copper")):
        return "B.Cu"

    inner_name = re.search(r"(?:inner|internal|in)[_-]?(\d+)(?:[_\.-]|$)", normalized)
    if inner_name:
        return f"In{int(inner_name.group(1))}.Cu"

    if any(k in normalized for k in ("f_mask", "top_mask", "soldermask_top")):
        return "F.Mask"
    if any(k in normalized for k in ("b_mask", "bottom_mask", "soldermask_bottom")):
        return "B.Mask"

    if any(k in normalized for k in ("f_silks", "top_silk", "legend_top")):
        return "F.SilkS"
    if any(k in normalized for k in ("b_silks", "bottom_silk", "legend_bottom")):
        return "B.SilkS"

    if "copper" in name and "bottom" not in name:
        return "F.Cu"
    if "bottom" in name and "copper" in name:
        return "B.Cu"

    return None


def infer_layer(path: str | Path, text: str | None = None) -> str | None:
    """Infer a layer unless immutable X2 FileFunction metadata is ambiguous."""
    source = text or ""
    if len(x2_file_function_declarations(source)) > 1:
        return None
    x2 = _x2_file_function_layer(source)
    if x2 is not None:
        return x2
    return _filename_layer(Path(path))
