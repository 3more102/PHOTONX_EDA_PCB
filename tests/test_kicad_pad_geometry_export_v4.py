import pytest

from photonx_eda_pcb.exporters.kicad import export_kicad_with_report
from photonx_eda_pcb.exporters.omission_manifest import omission_manifest
from photonx_eda_pcb.exporters.omission_validation import validate_omission_manifest
from photonx_eda_pcb.kicad_reader import read_kicad_board_text
from photonx_eda_pcb.models import BoardModel, PadCandidate, Point
from photonx_eda_pcb.roundtrip import compare_kicad_connectivity


@pytest.mark.parametrize(
    ("pad", "code"),
    [
        (
            PadCandidate(
                "P_BAD_COORD",
                Point(float("nan"), 0.0),
                1.0,
                1.0,
                "C",
                "F.Cu",
            ),
            "KICAD_PAD_COORDINATE_INVALID",
        ),
        (
            PadCandidate(
                "P_BAD_SIZE",
                Point(0.0, 0.0),
                0.0,
                1.0,
                "R",
                "F.Cu",
            ),
            "KICAD_PAD_SIZE_INVALID",
        ),
    ],
)
def test_invalid_pad_geometry_is_omitted_fail_closed(
    tmp_path,
    pad,
    code,
):
    board = BoardModel(pads=[pad])
    path, report = export_kicad_with_report(
        board,
        tmp_path / "pad.kicad_pcb",
    )
    text = path.read_text(encoding="utf-8")
    readback = read_kicad_board_text(text)
    audit = compare_kicad_connectivity(board, readback, report)

    assert "PHOTONX:RecoveredPad" not in text
    assert report.exported_pad_ids == []
    assert report.skipped_pad_ids == [pad.id]
    assert any(
        issue.code == code and issue.object_id == pad.id
        for issue in report.issues
    )
    assert audit["pads"]["equal"] is True
    assert audit["roundtrip_equal"] is True
    assert audit["source_connectivity_complete"] is False
    assert audit["source_equivalent"] is False
    assert audit["losses"]["skipped_pad_ids"] == [pad.id]
    assert validate_omission_manifest(omission_manifest(report)) == []


def test_nonfinite_pad_rotation_is_omitted_fail_closed(tmp_path):
    pad = PadCandidate(
        "P_BAD_ROT",
        Point(0.0, 0.0),
        1.0,
        1.0,
        "R",
        "F.Cu",
    )
    pad.rotation_deg = float("inf")
    board = BoardModel(pads=[pad])

    path, report = export_kicad_with_report(
        board,
        tmp_path / "pad.kicad_pcb",
    )
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))
    audit = compare_kicad_connectivity(board, readback, report)

    assert report.skipped_pad_ids == ["P_BAD_ROT"]
    assert any(
        issue.code == "KICAD_PAD_ROTATION_INVALID"
        for issue in report.issues
    )
    assert audit["pads"]["equal"] is True
    assert audit["source_equivalent"] is False


def test_invalid_pad_geometry_precedes_drill_padstack_claim(tmp_path):
    pad = PadCandidate(
        "P_BOTH",
        Point(float("nan"), 0.0),
        1.0,
        1.0,
        "C",
        "F.Cu",
        drill=0.8,
    )
    board = BoardModel(pads=[pad])

    _, report = export_kicad_with_report(
        board,
        tmp_path / "pad.kicad_pcb",
    )

    codes = {
        issue.code
        for issue in report.issues
        if issue.object_id == "P_BOTH"
    }
    assert codes == {"KICAD_PAD_COORDINATE_INVALID"}
