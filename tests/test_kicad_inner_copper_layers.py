from pathlib import Path

from photonx_eda_pcb.exporters.kicad import export_kicad_with_report
from photonx_eda_pcb.models import BoardModel, CopperRegion, Point, Track


def _inner_region() -> CopperRegion:
    return CopperRegion(
        "R_IN1",
        (
            Point(0, 0),
            Point(2, 0),
            Point(2, 1),
            Point(0, 1),
            Point(0, 0),
        ),
        "In1.Cu",
    )


def test_kicad_export_declares_observed_inner_copper_layers_and_exports_inner_zone(tmp_path: Path):
    board = BoardModel(
        tracks=[
            Track("T2", Point(0, 2), Point(1, 2), 0.2, "In2.Cu"),
            Track("T30", Point(0, 3), Point(1, 3), 0.2, "In30.Cu"),
        ],
        regions=[_inner_region()],
    )

    path, report = export_kicad_with_report(board, tmp_path / "inner.kicad_pcb")
    text = path.read_text(encoding="utf-8")

    expected_layers = [
        '    (0 "F.Cu" signal)',
        '    (1 "In1.Cu" signal)',
        '    (2 "In2.Cu" signal)',
        '    (30 "In30.Cu" signal)',
        '    (31 "B.Cu" signal)',
    ]
    positions = [text.index(layer) for layer in expected_layers]
    assert positions == sorted(positions)
    assert report.exported_regions == 1
    assert report.skipped_regions == 0
    assert '(layer "In1.Cu")' in text
    assert '(layer "In2.Cu")' in text
    assert '(layer "In30.Cu")' in text
    assert '(filled_polygon (layer "In1.Cu")' in text


def test_kicad_export_keeps_two_layer_table_when_no_inner_copper_is_observed(tmp_path: Path):
    board = BoardModel(
        tracks=[Track("T", Point(0, 0), Point(1, 0), 0.2, "F.Cu")]
    )

    path, report = export_kicad_with_report(board, tmp_path / "two_layer.kicad_pcb")
    text = path.read_text(encoding="utf-8")

    assert report.ok
    assert '    (0 "F.Cu" signal)' in text
    assert '    (31 "B.Cu" signal)' in text
    assert '"In1.Cu"' not in text


def test_noncanonical_region_layer_still_fails_closed(tmp_path: Path):
    region = CopperRegion(
        "R_BAD_LAYER",
        (
            Point(0, 0),
            Point(2, 0),
            Point(2, 1),
            Point(0, 1),
            Point(0, 0),
        ),
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
