import json

from photonx_eda_pcb.cli import _write_kicad_export_report
from photonx_eda_pcb.exporters.kicad_report import KicadExportIssue, KicadExportReport


def test_write_kicad_export_report_preserves_omissions_and_warnings(tmp_path):
    report = KicadExportReport(
        exported_slots=2,
        skipped_slots=1,
        skipped_regions=1,
        exported_npth_slots=1,
        exported_plated_slots=1,
        issues=[
            KicadExportIssue(
                "warning",
                "KICAD_SLOT_PLATING_UNKNOWN",
                "S1",
                "slot plating is unknown",
            )
        ],
        exported_slot_ids=["S0", "S2"],
        skipped_slot_ids=["S1"],
        skipped_region_ids=["R1"],
    )

    path = _write_kicad_export_report(tmp_path / "kicad_export_report.json", report)
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert payload["ok"] is True
    assert payload["exported_slots"] == 2
    assert payload["skipped_slots"] == 1
    assert payload["skipped_regions"] == 1
    assert payload["exported_slot_ids"] == ["S0", "S2"]
    assert payload["skipped_slot_ids"] == ["S1"]
    assert payload["skipped_region_ids"] == ["R1"]
    assert payload["issues"] == [
        {
            "severity": "warning",
            "code": "KICAD_SLOT_PLATING_UNKNOWN",
            "object_id": "S1",
            "message": "slot plating is unknown",
        }
    ]


def test_write_kicad_export_report_marks_error_report_not_ok(tmp_path):
    report = KicadExportReport(
        issues=[KicadExportIssue("error", "KICAD_EXPORT_ERROR", "P1", "failed")]
    )

    path = _write_kicad_export_report(tmp_path / "report.json", report)
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert payload["ok"] is False
