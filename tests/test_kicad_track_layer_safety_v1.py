from photonx_eda_pcb.exporters.kicad import export_kicad_with_report
from photonx_eda_pcb.exporters.omission_manifest import omission_manifest
from photonx_eda_pcb.exporters.omission_validation import validate_omission_manifest
from photonx_eda_pcb.models import BoardModel, Point, Track


def test_noncanonical_inner_track_layer_is_omitted(tmp_path):
    board = BoardModel(
        tracks=[
            Track(
                "T_BAD",
                Point(0, 0),
                Point(1, 0),
                0.2,
                "In31.Cu",
            )
        ]
    )

    path, report = export_kicad_with_report(
        board,
        tmp_path / "invalid-track-layer.kicad_pcb",
    )
    text = path.read_text(encoding="utf-8")

    assert '"In31.Cu" signal' not in text
    assert '(layer "In31.Cu")' not in text
    assert "(segment " not in text
    assert report.exported_tracks == 0
    assert report.skipped_tracks == 1
    assert report.skipped_track_ids == ["T_BAD"]
    assert any(
        issue.code == "KICAD_TRACK_LAYER_UNSUPPORTED"
        and issue.object_id == "T_BAD"
        for issue in report.issues
    )

    manifest = omission_manifest(report)
    assert manifest["skipped_tracks"] == ["T_BAD"]
    assert validate_omission_manifest(manifest) == []


def test_arbitrary_non_copper_track_layer_is_omitted(tmp_path):
    board = BoardModel(
        tracks=[
            Track(
                "T_BAD",
                Point(0, 0),
                Point(1, 0),
                0.2,
                "Dwgs.User",
            )
        ]
    )

    path, report = export_kicad_with_report(
        board,
        tmp_path / "user-layer-track.kicad_pcb",
    )
    text = path.read_text(encoding="utf-8")

    assert '(layer "Dwgs.User")' not in text
    assert "(segment " not in text
    assert report.skipped_track_ids == ["T_BAD"]
    assert any(
        issue.code == "KICAD_TRACK_LAYER_UNSUPPORTED"
        for issue in report.issues
    )


def test_canonical_inner_track_layer_still_exports(tmp_path):
    board = BoardModel(
        tracks=[
            Track(
                "T_OK",
                Point(0, 0),
                Point(1, 0),
                0.2,
                "In3.Cu",
            )
        ]
    )

    path, report = export_kicad_with_report(
        board,
        tmp_path / "canonical-inner-track.kicad_pcb",
    )
    text = path.read_text(encoding="utf-8")

    assert '    (1 "In1.Cu" signal)' in text
    assert '    (2 "In2.Cu" signal)' in text
    assert '    (3 "In3.Cu" signal)' in text
    assert '(layer "In3.Cu")' in text
    assert "(segment " in text
    assert report.exported_track_ids == ["T_OK"]
    assert report.skipped_tracks == 0


def test_bad_layer_and_unresolved_net_report_both_but_skip_once(tmp_path):
    board = BoardModel(
        tracks=[
            Track(
                "T_BAD",
                Point(0, 0),
                Point(1, 0),
                0.2,
                "In31.Cu",
                net_id="MISSING",
            )
        ]
    )

    _, report = export_kicad_with_report(
        board,
        tmp_path / "two-reasons-one-skip.kicad_pcb",
    )

    assert report.skipped_tracks == 1
    assert report.skipped_track_ids == ["T_BAD"]
    codes = {
        issue.code
        for issue in report.issues
        if issue.object_id == "T_BAD"
    }
    assert "KICAD_TRACK_LAYER_UNSUPPORTED" in codes
    assert "KICAD_NET_REFERENCE_UNRESOLVED" in codes
    assert validate_omission_manifest(omission_manifest(report)) == []
