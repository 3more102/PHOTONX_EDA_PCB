from __future__ import annotations

import json
from pathlib import Path

from ..models import BoardModel
from ..reporting import summary
from ..roundtrip import board_fingerprint_manifest
from ..validation import ValidationReport


def write_reconstruction_bundle(
    board: BoardModel,
    report: ValidationReport,
    directory: str | Path,
) -> Path:
    root = Path(directory)
    root.mkdir(parents=True, exist_ok=True)

    (root / "board.json").write_text(
        json.dumps(board.to_dict(), indent=2, sort_keys=True),
        encoding="utf-8",
    )

    validation = {
        "ok": report.ok,
        "issues": [issue.__dict__ for issue in report.issues],
        "summary": summary(board, report),
    }
    (root / "validation.json").write_text(
        json.dumps(validation, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    fingerprint = board_fingerprint_manifest(board)
    fingerprint["summary"] = summary(board, report)
    (root / "fingerprint.json").write_text(
        json.dumps(fingerprint, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return root
