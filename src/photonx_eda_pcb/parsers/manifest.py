from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from .layer_map import infer_layer


@dataclass(frozen=True)
class ManufacturingFile:
    path: Path
    kind: str
    layer: str | None = None


def discover_manufacturing_files(directory: str | Path) -> list[ManufacturingFile]:
    root = Path(directory)
    result = []
    for p in sorted(x for x in root.iterdir() if x.is_file()):
        suffix = p.suffix.lower()
        if suffix in {".drl", ".xnc", ".exc"} or "drill" in p.name.lower():
            result.append(ManufacturingFile(p, "drill")); continue
        layer = infer_layer(p)
        if suffix in {".gbr", ".ger", ".gtl", ".gbl", ".gts", ".gbs", ".gto", ".gbo", ".gm1", ".gko"} or layer:
            result.append(ManufacturingFile(p, "gerber", layer))
    return result
