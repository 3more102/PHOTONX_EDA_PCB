from photonx_eda_pcb.exporters.kicad import export_kicad_with_report
from photonx_eda_pcb.exporters.omission_manifest import omission_manifest
from photonx_eda_pcb.exporters.omission_validation import validate_omission_manifest
from photonx_eda_pcb.kicad_reader import read_kicad_board_text
from photonx_eda_pcb.models import BoardModel, DrillHit, Point
from photonx_eda_pcb.roundtrip import compare_kicad_connectivity


def test_nonplated_point_drill_exports_and_roundtrips(tmp_path):
    board = BoardModel(
        drills=[
            DrillHit(
                "D1",
                Point(1.25, 2.5),
                0.8,
                "non-plated",
            )
        ]
    )
    path, report = export_kicad_with_report(
        board,
        tmp_path / "drill.kicad_pcb",
    )
    text = path.read_text(encoding="utf-8")
    readback = read_kicad_board_text(text)
    audit = compare_kicad_connectivity(board, readback, report)

    assert 'PHOTONX:RecoveredNPTHDrill' in text
    assert '(pad "" np_thru_hole circle' in text
    assert '(drill 0.800000)' in text
    assert report.exported_drill_ids == ["D1"]
    assert report.skipped_drill_ids == []
    assert audit["drills"]["equal"] is True
    assert audit["drills"]["expected_count"] == 1
    assert audit["roundtrip_equal"] is True
    assert audit["source_equivalent"] is True
    assert validate_omission_manifest(omission_manifest(report)) == []


def test_unknown_point_drill_is_explicit_source_loss(tmp_path):
    board = BoardModel(
        drills=[DrillHit("D1", Point(0, 0), 0.6, "unknown")]
    )
    path, report = export_kicad_with_report(
        board,
        tmp_path / "drill.kicad_pcb",
    )
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))
    audit = compare_kicad_connectivity(board, readback, report)

    assert report.exported_drill_ids == []
    assert report.skipped_drill_ids == ["D1"]
    assert any(
        issue.code == "KICAD_DRILL_PLATING_UNKNOWN"
        and issue.object_id == "D1"
        for issue in report.issues
    )
    assert audit["drills"]["equal"] is True
    assert audit["roundtrip_equal"] is True
    assert audit["source_connectivity_complete"] is False
    assert audit["source_equivalent"] is False
    assert audit["losses"]["skipped_drill_ids"] == ["D1"]
    assert validate_omission_manifest(omission_manifest(report)) == []


def test_plated_point_drill_is_not_mislabeled_npth(tmp_path):
    board = BoardModel(
        drills=[DrillHit("D1", Point(0, 0), 0.6, "plated")]
    )
    path, report = export_kicad_with_report(
        board,
        tmp_path / "drill.kicad_pcb",
    )
    text = path.read_text(encoding="utf-8")

    assert 'PHOTONX:RecoveredNPTHDrill' not in text
    assert report.skipped_drill_ids == ["D1"]
    assert any(
        issue.code == "KICAD_DRILL_PLATED_PADSTACK_UNSUPPORTED"
        and issue.object_id == "D1"
        for issue in report.issues
    )


def test_point_drill_roundtrip_detects_geometry_drift(tmp_path):
    board = BoardModel(
        drills=[
            DrillHit(
                "D1",
                Point(1.0, 2.0),
                0.8,
                "non-plated",
            )
        ]
    )
    path, report = export_kicad_with_report(
        board,
        tmp_path / "drill.kicad_pcb",
    )
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))
    footprint = next(
        item
        for item in readback["footprints"]
        if item["name"] == "PHOTONX:RecoveredNPTHDrill"
    )
    footprint["pads"][0]["drill_size"] = (0.9, 0.9)

    audit = compare_kicad_connectivity(board, readback, report)

    assert audit["drills"]["equal"] is False
    assert audit["roundtrip_equal"] is False


def test_route_omission_participates_in_source_equivalence(tmp_path):
    from photonx_eda_pcb.excellon_routing.model import RoutedPath

    board = BoardModel(
        routes=[
            RoutedPath(
                "ROUTE1",
                ((0.0, 0.0), (2.0, 0.0)),
                0.8,
                "unknown",
                "T01",
            )
        ]
    )
    path, report = export_kicad_with_report(
        board,
        tmp_path / "route.kicad_pcb",
    )
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))
    audit = compare_kicad_connectivity(board, readback, report)

    assert report.skipped_route_ids == ["ROUTE1"]
    assert audit["roundtrip_equal"] is True
    assert audit["losses"]["omitted_route_ids"] == ["ROUTE1"]
    assert audit["source_connectivity_complete"] is False
    assert audit["source_equivalent"] is False
