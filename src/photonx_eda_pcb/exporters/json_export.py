from __future__ import annotations
import json
from pathlib import Path
from ..models import BoardModel
from ..io.safe_write import atomic_write_text


def export_json(board: BoardModel, path: str | Path) -> Path:
    p = Path(path)
    return atomic_write_text(
        p,
        json.dumps(board.to_dict(), indent=2, sort_keys=True),
    )
