from photonx_eda_pcb.exporters.kicad import export_kicad_with_report
from photonx_eda_pcb.models import BoardModel, CopperRegion, PadCandidate, Point, Track


def test_kicad_export_declares_observed_inner_copper_layers_in_ordinal_order(tmp_path):
    board = BoardModel(
        tracks=[
            Track("T2", Point(0, 0), Point(1, 0), 0.2, "In2.Cu"),
        ],
        pads=[
            PadCandidate("P1", Point(2, 0), 1.0, 1.0, "R", "In1.Cu"),
        ],
        regions=[
            CopperRegion(
                "R30",
                (Point(0, 2), Point(2, 2), Point(1, 3)),
                "In30.Cu",
            ),
        ],
    )

    path, report = export_kicad_with_report(board, tmp_path / "inner.kicad_pcb")
    text = path.read_text(encoding="utf-8")

    assert report.ok
    expected_layers = [
        '    (0 "F.Cu" signal)',
        '    (1 "In1.Cu" signal)',
        '    (2 "In2.Cu" signal)',
        '    (30 "In30.Cu" signal)',
        '    (31 "B.Cu" signal)',
    ]
    positions = [text.index(layer) for layer in expected_layers]
    assert positions == sorted(positions)
    assert all(text.count(layer) == 1 for layer in expected_layers)
    assert '(layer "In1.Cu")' in text
    assert '(layer "In2.Cu")' in text
    assert '(layer "In30.Cu")' in text


def test_kicad_export_allows_simple_region_zone_on_declared_inner_copper(tmp_path):
    region = CopperRegion(
        "R3",
        (Point(0, 0), Point(3, 0), Point(3, 2), Point(0, 2)),
        "In3.Cu",
    )
    board = BoardModel(regions=[region])

    path, report = export_kicad_with_report(board, tmp_path / "inner-zone.kicad_pcb")
    text = path.read_text(encoding="utf-8")

    assert report.ok
    assert report.exported_regions == 1
    assert report.exported_region_ids == ["R3"]
    assert '    (3 "In3.Cu" signal)' in text
    assert '(layer "In3.Cu")' in text
    assert "KICAD_COPPER_REGION_LAYER_UNSUPPORTED" not in {issue.code for issue in report.issues}


def test_kicad_export_keeps_two_layer_table_without_inner_copper(tmp_path):
    board = BoardModel(
        tracks=[Track("T", Point(0, 0), Point(1, 0), 0.2, "F.Cu")]
    )

    path, report = export_kicad_with_report(board, tmp_path / "two-layer.kicad_pcb")
    text = path.read_text(encoding="utf-8")

    assert report.ok
    assert '    (0 "F.Cu" signal)' in text
    assert '    (31 "B.Cu" signal)' in text
    assert '"In1.Cu"' not in text


def test_kicad_export_rejects_noncanonical_region_layer(tmp_path):
    region = CopperRegion(
        "R_BAD_LAYER",
        (Point(0, 0), Point(2, 0), Point(2, 1), Point(0, 1)),
        "Inner1.Cu",
    )

    path, report = export_kicad_with_report(
        BoardModel(regions=[region]),
        tmp_path / "bad-layer.kicad_pcb",
    )
    text = path.read_text(encoding="utf-8")

    assert report.exported_regions == 0
    assert report.skipped_regions == 1
    assert "R_BAD_LAYER" not in text
    assert any(
        issue.code == "KICAD_COPPER_REGION_LAYER_UNSUPPORTED"
        and issue.object_id == "R_BAD_LAYER"
        for issue in report.issues
    )
