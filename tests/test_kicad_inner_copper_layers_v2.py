from photonx_eda_pcb.exporters.kicad import export_kicad_with_report
from photonx_eda_pcb.models import BoardModel, CopperRegion, Point, Track


def _region(layer: str) -> CopperRegion:
    return CopperRegion(
        "R1",
        (
            Point(0, 0),
            Point(2, 0),
            Point(2, 1),
            Point(0, 1),
            Point(0, 0),
        ),
        layer,
    )


def test_kicad_export_declares_observed_inner_copper_layers(tmp_path):
    board = BoardModel(
        tracks=[
            Track("T2", Point(0, 0), Point(1, 0), 0.2, "In2.Cu"),
            Track("T1", Point(0, 1), Point(1, 1), 0.2, "In1.Cu"),
            Track("T30", Point(0, 2), Point(1, 2), 0.2, "In30.Cu"),
        ]
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
    for index in range(1, 31):
        assert text.count(f'({index} "In{index}.Cu" signal)') == 1
    assert '(layer "In1.Cu")' in text
    assert '(layer "In2.Cu")' in text
    assert '(layer "In30.Cu")' in text



def test_highest_observed_inner_layer_implies_contiguous_stack_prefix(tmp_path):
    board = BoardModel(
        tracks=[Track("T3", Point(0, 0), Point(1, 0), 0.2, "In3.Cu")]
    )

    path, report = export_kicad_with_report(board, tmp_path / "inner_prefix.kicad_pcb")
    text = path.read_text(encoding="utf-8")

    assert report.ok
    assert '    (1 "In1.Cu" signal)' in text
    assert '    (2 "In2.Cu" signal)' in text
    assert '    (3 "In3.Cu" signal)' in text
    assert '"In4.Cu" signal' not in text


def test_inner_copper_region_exports_as_declared_zone(tmp_path):
    path, report = export_kicad_with_report(
        BoardModel(regions=[_region("In2.Cu")]),
        tmp_path / "inner_region.kicad_pcb",
    )
    text = path.read_text(encoding="utf-8")

    assert report.exported_regions == 1
    assert report.skipped_regions == 0
    assert '    (2 "In2.Cu" signal)' in text
    assert '(layer "In2.Cu")' in text
    assert not any(
        issue.code == "KICAD_COPPER_REGION_LAYER_UNSUPPORTED"
        for issue in report.issues
    )


def test_noncanonical_inner_layer_is_not_declared_or_used_for_region_zone(tmp_path):
    path, report = export_kicad_with_report(
        BoardModel(regions=[_region("In31.Cu")]),
        tmp_path / "invalid_inner_region.kicad_pcb",
    )
    text = path.read_text(encoding="utf-8")

    assert report.exported_regions == 0
    assert report.skipped_regions == 1
    assert '"In31.Cu" signal' not in text
    assert any(
        issue.code == "KICAD_COPPER_REGION_LAYER_UNSUPPORTED"
        and issue.object_id == "R1"
        for issue in report.issues
    )


def test_kicad_export_keeps_two_layer_table_without_inner_copper(tmp_path):
    board = BoardModel(
        tracks=[Track("T", Point(0, 0), Point(1, 0), 0.2, "F.Cu")]
    )

    path, report = export_kicad_with_report(board, tmp_path / "two_layer.kicad_pcb")
    text = path.read_text(encoding="utf-8")

    assert report.ok
    assert '    (0 "F.Cu" signal)' in text
    assert '    (31 "B.Cu" signal)' in text
    assert '"In1.Cu"' not in text
