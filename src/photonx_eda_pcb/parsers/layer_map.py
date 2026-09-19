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
_FILE_FUNCTION_PRESENT = re.compile(r"%TF\.FileFunction(?=[,*%])", re.IGNORECASE)


def _side_token(tokens: list[str]) -> str | None:
    sides = set()
    for token in tokens:
        if token in {"top", "front"}:
            sides.add("top")
        elif token in {"bot", "bottom", "back"}:
            sides.add("bottom")
        elif token == "inr":
            sides.add("inner")
    return next(iter(sides)) if len(sides) == 1 else None


def _positive_index(token: str) -> bool:
    return bool(re.fullmatch(r"[1-9]\d*", token))


def _x2_file_function_layer(text: str) -> str | None:
    source = text or ""
    if len(list(_FILE_FUNCTION_PRESENT.finditer(source))) != 1:
        return None
    match = _FILE_FUNCTION.search(source)
    if not match:
        return None

    parts = [p.strip() for p in match.group("value").split(",")]
    if not parts or any(not p for p in parts):
        return None

    function = parts[0].lower()
    tokens = [p.lower() for p in parts[1:]]

    if function == "copper":
        if len(tokens) not in {2, 3}:
            return None
        layer_match = re.fullmatch(r"l([1-9]\d*)", tokens[0])
        if not layer_match:
            return None
        layer_number = int(layer_match.group(1))
        side = _side_token([tokens[1]])
        if side is None:
            return None
        if len(tokens) == 3 and tokens[2] not in {"plane", "signal", "mixed", "hatched"}:
            return None
        if side == "top":
            return "F.Cu" if layer_number == 1 else None
        if side == "inner":
            return f"In{layer_number - 1}.Cu" if layer_number > 1 else None
        return "B.Cu" if layer_number > 1 else None

    if function in {"soldermask", "solder_mask", "legend", "silkscreen"}:
        if len(tokens) not in {1, 2}:
            return None
        side = _side_token([tokens[0]])
        if side not in {"top", "bottom"}:
            return None
        if len(tokens) == 2 and not _positive_index(tokens[1]):
            return None
        if function in {"soldermask", "solder_mask"}:
            return "F.Mask" if side == "top" else "B.Mask"
        return "F.SilkS" if side == "top" else "B.SilkS"

    if function == "paste":
        if len(tokens) != 1:
            return None
        side = _side_token(tokens)
        if side not in {"top", "bottom"}:
            return None
        return "F.Paste" if side == "top" else "B.Paste"

    if function == "profile":
        if len(tokens) != 1 or tokens[0] not in {"p", "np"}:
            return None
        return "Edge.Cuts"

    # Preserve the historical non-standard alias rather than treating it as an
    # unrecognized FileFunction and falling back to filename inference.
    if function == "outline":
        return "Edge.Cuts" if not tokens else None

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
    """Infer a KiCad-like layer from X2 metadata first, then filename hints."""
    source = text or ""
    x2 = _x2_file_function_layer(source)
    if x2 is not None:
        return x2
    if _FILE_FUNCTION_PRESENT.search(source):
        return None
    return _filename_layer(Path(path))
