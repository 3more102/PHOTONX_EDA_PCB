from __future__ import annotations
from pathlib import Path

_SUFFIXES = {
    ".gtl": "F.Cu", ".gbl": "B.Cu", ".gts": "F.Mask", ".gbs": "B.Mask",
    ".gto": "F.SilkS", ".gbo": "B.SilkS", ".gm1": "Edge.Cuts", ".gko": "Edge.Cuts",
}


def infer_layer(path: str | Path) -> str | None:
    p = Path(path)
    suffix = p.suffix.lower()
    if suffix in _SUFFIXES: return _SUFFIXES[suffix]
    n = p.name.lower()
    if "outline" in n or "edge" in n: return "Edge.Cuts"
    if "copper" in n and "bottom" not in n: return "F.Cu"
    if "bottom" in n and "copper" in n: return "B.Cu"
    return None
