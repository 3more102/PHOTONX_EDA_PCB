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
    # Common legacy Protel/Altium naming.
    ".cmp": "F.Cu",
    ".sol": "B.Cu",
}

_FILE_FUNCTION = re.compile(
    r"%TF\.FileFunction,(?P<value>[^*%]+)\*%",
    re.IGNORECASE,
)


def _x2_file_function_layer(text: str) -> str | None:
    match = _FILE_FUNCTION.search(text or "")
    if not match:
        return None

    parts = [p.strip() for p in match.group("value").split(",") if p.strip()]
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
            # Without an explicit side, retain the layer as an inner-copper
            # identity rather than guessing that it is the bottom layer.
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

    name = path.name.lower()
    normalized = re.sub(r"[^a-z0-9]+", "_", name)

    if any(k in normalized for k in ("outline", "edge_cuts", "board_edge", "profile")):
        return "Edge.Cuts"

    if any(k in normalized for k in ("f_cu", "top_copper", "copper_top", "front_copper")):
        return "F.Cu"
    if any(k in normalized for k in ("b_cu", "bottom_copper", "copper_bottom", "back_copper")):
        return "B.Cu"

    if any(k in normalized for k in ("f_mask", "top_mask", "soldermask_top")):
        return "F.Mask"
    if any(k in normalized for k in ("b_mask", "bottom_mask", "soldermask_bottom")):
        return "B.Mask"

    if any(k in normalized for k in ("f_silks", "top_silk", "legend_top")):
        return "F.SilkS"
    if any(k in normalized for k in ("b_silks", "bottom_silk", "legend_bottom")):
        return "B.SilkS"

    # Preserve the earlier simple naming convention.
    if "copper" in name and "bottom" not in name:
        return "F.Cu"
    if "bottom" in name and "copper" in name:
        return "B.Cu"

    return None


def infer_layer(path: str | Path, text: str | None = None) -> str | None:
    """Infer a KiCad-like layer from X2 metadata first, then filename hints."""

    x2 = _x2_file_function_layer(text or "")
    if x2 is not None:
        return x2
    return _filename_layer(Path(path))
