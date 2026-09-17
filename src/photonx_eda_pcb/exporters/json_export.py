from __future__ import annotations
import json
from pathlib import Path
from ..models import BoardModel


def export_json(board: BoardModel, path: str | Path) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(board.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    return p
