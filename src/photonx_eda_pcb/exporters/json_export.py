from __future__ import annotations

from pathlib import Path

from ..models import BoardModel
from ..serialization.json_policy import dumps_strict


def export_json(board: BoardModel, path: str | Path) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        dumps_strict(board.to_dict(), indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return p
