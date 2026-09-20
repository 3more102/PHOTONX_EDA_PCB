from photonx_eda_pcb.exporters.kicad import export_kicad_with_report
from photonx_eda_pcb.models import BoardModel, DrillHit, NetGroup, PadCandidate, Point, Track


def _x2_four_layer_metadata():
    return {
        "status": "declared",
        "declared_copper_count": 4,
        "layers": ["F.Cu", "In1.Cu", "In2.Cu", "B.Cu"],
    }


def _pad(pad_id, layer):
    return PadCandidate(
        pad_id,
        Point(0, 0),
        1.0,
        1.0,
        "C",
        layer,
        None,
        "N1",
    )


def test_x2_declared_stackup_is_emitted_even_when_inner_geometry_is_absent(tmp_path):
    board = BoardModel(
        tracks=[Track("T_F", Point(0, 0), Point(1, 0), 0.2, "F.Cu")],
        metadata={"x2_copper_stackup": _x2_four_layer_metadata()},
    )

    path, report = export_kicad_with_report(
        board,
        tmp_path / "x2_stackup.kicad_pcb",
    )
    text = path.read_text(encoding="utf-8")

    assert report.ok
    assert '    (0 "F.Cu" signal)' in text
    assert '    (1 "In1.Cu" signal)' in text
    assert '    (2 "In2.Cu" signal)' in text
    assert '    (31 "B.Cu" signal)' in text


def test_x2_declared_inner_layers_block_via_export_without_full_support(tmp_path):
    board = BoardModel(
        nets=[NetGroup("N1", [], 1.0, "GND")],
        pads=[
            _pad("P_F", "F.Cu"),
            _pad("P_B", "B.Cu"),
        ],
        drills=[DrillHit("D1", Point(0, 0), 0.4, "plated")],
        metadata={
            "x2_copper_stackup": _x2_four_layer_metadata(),
            "via_spans": [
                {
                    "drill_id": "D1",
                    "from_layer": "F.Cu",
                    "to_layer": "B.Cu",
                    "confidence": 0.95,
                    "proven": True,
                    "pad_ids": ["P_F", "P_B"],
                    "layer_ids": ["F.Cu", "In1.Cu", "In2.Cu", "B.Cu"],
                    "evidence": ["X2-declared four-layer stackup"],
                }
            ],
        },
    )

    path, report = export_kicad_with_report(
        board,
        tmp_path / "x2_via_guard.kicad_pcb",
    )
    text = path.read_text(encoding="utf-8")

    assert '    (1 "In1.Cu" signal)' in text
    assert '    (2 "In2.Cu" signal)' in text
    assert "(via " not in text
    assert report.exported_via_span_ids == []
    assert report.skipped_via_span_ids == ["D1"]
    assert any(
        issue.code == "KICAD_PROVEN_VIA_LAYER_SUPPORT_INCOMPLETE"
        and issue.object_id == "D1"
        for issue in report.issues
    )


def test_malformed_declared_x2_stackup_is_not_promoted_into_kicad_layers(tmp_path):
    board = BoardModel(
        tracks=[Track("T_F", Point(0, 0), Point(1, 0), 0.2, "F.Cu")],
        metadata={
            "x2_copper_stackup": {
                "status": "declared",
                "declared_copper_count": 4,
                "layers": ["F.Cu", "In2.Cu", "In1.Cu", "B.Cu"],
            }
        },
    )

    path, report = export_kicad_with_report(
        board,
        tmp_path / "bad_x2_stackup.kicad_pcb",
    )
    text = path.read_text(encoding="utf-8")

    assert report.ok
    assert '"In1.Cu"' not in text
    assert '"In2.Cu"' not in text
