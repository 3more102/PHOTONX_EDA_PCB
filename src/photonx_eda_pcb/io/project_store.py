from __future__ import annotations
import json
from pathlib import Path
from ..models import BoardModel
from ..reporting import summary
from ..validation import ValidationReport
from .safe_write import atomic_write_text


def write_reconstruction_bundle(board: BoardModel, report: ValidationReport, directory: str | Path) -> Path:
    root = Path(directory); root.mkdir(parents=True, exist_ok=True)
    atomic_write_text(root / "board.json", json.dumps(board.to_dict(), indent=2, sort_keys=True))
    validation = {"ok": report.ok, "issues": [issue.__dict__ for issue in report.issues], "summary": summary(board, report)}
    atomic_write_text(root / "validation.json", json.dumps(validation, indent=2, sort_keys=True))
    return root
