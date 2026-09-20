import pytest

from photonx_eda_pcb.exporters.kicad import export_kicad_with_report
from photonx_eda_pcb.exporters.omission_manifest import omission_manifest
from photonx_eda_pcb.exporters.omission_validation import validate_omission_manifest
from photonx_eda_pcb.kicad_reader import read_kicad_board_text
from photonx_eda_pcb.models import BoardModel, Point, Track
from photonx_eda_pcb.roundtrip import compare_kicad_connectivity


@pytest.mark.parametrize(
    ("track", "code"),
    [
        (
            Track(
                "T_BAD_COORD",
                Point(float("nan"), 0.0),
                Point(1.0, 0.0),
                0.2,
                "F.Cu",
            ),
            "KICAD_TRACK_COORDINATE_INVALID",
        ),
        (
            Track(
                "T_BAD_WIDTH",
                Point(0.0, 0.0),
                Point(1.0, 0.0),
                0.0,
                "F.Cu",
            ),
            "KICAD_TRACK_WIDTH_INVALID",
        ),
        (
            Track(
                "T_ZERO",
                Point(1.0, 1.0),
                Point(1.0, 1.0),
                0.2,
                "F.Cu",
            ),
            "KICAD_TRACK_ZERO_LENGTH",
        ),
    ],
)
def test_invalid_track_geometry_is_omitted_fail_closed(
    tmp_path,
    track,
    code,
):
    board = BoardModel(tracks=[track])
    path, report = export_kicad_with_report(
        board,
        tmp_path / "track.kicad_pcb",
    )
    text = path.read_text(encoding="utf-8")
    readback = read_kicad_board_text(text)
    audit = compare_kicad_connectivity(board, readback, report)

    assert "(segment " not in text
    assert report.exported_track_ids == []
    assert report.skipped_track_ids == [track.id]
    assert any(
        issue.code == code and issue.object_id == track.id
        for issue in report.issues
    )
    assert audit["tracks"]["equal"] is True
    assert audit["roundtrip_equal"] is True
    assert audit["source_connectivity_complete"] is False
    assert audit["source_equivalent"] is False
    assert audit["losses"]["skipped_track_ids"] == [track.id]
    assert validate_omission_manifest(omission_manifest(report)) == []


def test_invalid_track_geometry_and_net_each_remain_diagnostic(tmp_path):
    track = Track(
        "T_BOTH",
        Point(0.0, 0.0),
        Point(1.0, 0.0),
        -0.2,
        "F.Cu",
        "MISSING",
    )
    board = BoardModel(tracks=[track])

    _, report = export_kicad_with_report(
        board,
        tmp_path / "track.kicad_pcb",
    )

    assert report.skipped_track_ids == ["T_BOTH"]
    codes = {
        issue.code
        for issue in report.issues
        if issue.object_id == "T_BOTH"
    }
    assert "KICAD_TRACK_WIDTH_INVALID" in codes
    assert "KICAD_NET_REFERENCE_UNRESOLVED" in codes
