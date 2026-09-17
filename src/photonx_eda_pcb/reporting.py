from __future__ import annotations
from .models import BoardModel
from .validation import ValidationReport


def summary(board: BoardModel, report: ValidationReport | None = None) -> dict[str, object]:
    data = {"tracks": len(board.tracks), "pads": len(board.pads), "drills": len(board.drills), "outline_segments": len(board.outline), "physical_nets": len(board.nets), "component_hypotheses": len(board.components), "parse_diagnostics": len(board.diagnostics)}
    if report is not None:
        data.update({"validation_ok": report.ok, "errors": len(report.errors), "warnings": len(report.warnings)})
    return data
