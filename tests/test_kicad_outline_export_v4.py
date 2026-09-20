import pytest

from photonx_eda_pcb.exporters.kicad import export_kicad_with_report
from photonx_eda_pcb.exporters.omission_manifest import omission_manifest
from photonx_eda_pcb.exporters.omission_validation import validate_omission_manifest
from photonx_eda_pcb.kicad_reader import read_kicad_board_text
from photonx_eda_pcb.models import BoardModel, OutlineSegment, Point
from photonx_eda_pcb.roundtrip import compare_kicad_connectivity


@pytest.mark.parametrize("bad_value", [float("nan"), float("inf"), "bad", None])
def test_invalid_outline_coordinate_is_omitted_fail_closed(tmp_path, bad_value):
    board = BoardModel(
        outline=[
            OutlineSegment(
                "E_BAD",
                Point(bad_value, 0.0),
                Point(1.0, 0.0),
            )
        ]
    )

    path, report = export_kicad_with_report(
        board,
        tmp_path / "outline.kicad_pcb",
    )
    text = path.read_text(encoding="utf-8")
    readback = read_kicad_board_text(text)
    audit = compare_kicad_connectivity(board, readback, report)

    assert "(gr_line " not in text
    assert report.exported_outline_ids == []
    assert report.skipped_outline_ids == ["E_BAD"]
    assert any(
        issue.code == "KICAD_OUTLINE_COORDINATE_INVALID"
        for issue in report.issues
    )
    assert audit["outline"]["equal"] is True
    assert audit["roundtrip_equal"] is True
    assert audit["source_connectivity_complete"] is False
    assert audit["source_equivalent"] is False
    assert audit["losses"]["skipped_outline_ids"] == ["E_BAD"]
    assert validate_omission_manifest(omission_manifest(report)) == []


def test_zero_length_outline_is_omitted_fail_closed(tmp_path):
    board = BoardModel(
        outline=[
            OutlineSegment(
                "E_ZERO",
                Point(1.0, 2.0),
                Point(1.0, 2.0),
            )
        ]
    )

    path, report = export_kicad_with_report(
        board,
        tmp_path / "outline.kicad_pcb",
    )
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))
    audit = compare_kicad_connectivity(board, readback, report)

    assert report.skipped_outline_ids == ["E_ZERO"]
    assert any(
        issue.code == "KICAD_OUTLINE_ZERO_LENGTH"
        for issue in report.issues
    )
    assert audit["outline"]["equal"] is True
    assert audit["roundtrip_equal"] is True
    assert audit["source_connectivity_complete"] is False
    assert audit["source_equivalent"] is False


def test_mixed_valid_and_invalid_outline_exports_only_valid_subset(tmp_path):
    board = BoardModel(
        outline=[
            OutlineSegment("E1", Point(0.0, 0.0), Point(2.0, 0.0)),
            OutlineSegment("E_BAD", Point(float("nan"), 0.0), Point(1.0, 1.0)),
        ]
    )

    path, report = export_kicad_with_report(
        board,
        tmp_path / "outline.kicad_pcb",
    )
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))
    audit = compare_kicad_connectivity(board, readback, report)

    assert report.exported_outline_ids == ["E1"]
    assert report.skipped_outline_ids == ["E_BAD"]
    assert audit["outline"]["equal"] is True
    assert audit["outline"]["expected_count"] == 1
    assert audit["outline"]["observed_count"] == 1
    assert audit["roundtrip_equal"] is True
    assert audit["source_equivalent"] is False
