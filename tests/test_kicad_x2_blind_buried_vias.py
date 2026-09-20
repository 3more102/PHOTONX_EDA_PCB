from photonx_eda_pcb.exporters.kicad import export_kicad_with_report
from photonx_eda_pcb.kicad_reader import read_kicad_board_text
from photonx_eda_pcb.models import BoardModel, DrillHit, NetGroup, PadCandidate, Point
from photonx_eda_pcb.roundtrip.kicad_connectivity import compare_kicad_connectivity


def _net():
    return NetGroup("N1", [], 1.0, "SIG")


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


def _board(kind, from_layer, to_layer, layers, x2_layer_span):
    pad_ids = [f"P{index}" for index, _layer in enumerate(layers, start=1)]
    return BoardModel(
        nets=[_net()],
        pads=[
            _pad(pad_id, layer)
            for pad_id, layer in zip(pad_ids, layers)
        ],
        drills=[
            DrillHit(
                "D1",
                Point(0, 0),
                0.4,
                "plated",
                x2_layer_span=x2_layer_span,
                x2_span_kind=kind,
            )
        ],
        metadata={
            "via_spans": [
                {
                    "drill_id": "D1",
                    "from_layer": from_layer,
                    "to_layer": to_layer,
                    "confidence": 0.99,
                    "proven": True,
                    "pad_ids": pad_ids,
                    "layer_ids": list(layers),
                    "evidence": ["explicit X2 plated span"],
                }
            ]
        },
    )


def test_x2_blind_via_exports_with_exact_kicad_type(tmp_path):
    board = _board(
        "blind",
        "F.Cu",
        "In1.Cu",
        ("F.Cu", "In1.Cu"),
        (1, 2),
    )

    path, report = export_kicad_with_report(
        board,
        tmp_path / "blind.kicad_pcb",
    )
    text = path.read_text(encoding="utf-8")
    readback = read_kicad_board_text(text)
    audit = compare_kicad_connectivity(board, readback, report)

    assert "(via blind " in text
    assert len(readback["vias"]) == 1
    assert readback["vias"][0]["type"] == "blind"
    assert readback["vias"][0]["layers"] == ("F.Cu", "In1.Cu")
    assert report.exported_via_span_ids == ["D1"]
    assert report.skipped_via_span_ids == []
    assert audit["vias"]["equal"] is True
    assert audit["source_equivalent"] is True


def test_x2_buried_via_exports_with_exact_kicad_type(tmp_path):
    board = _board(
        "buried",
        "In1.Cu",
        "In2.Cu",
        ("In1.Cu", "In2.Cu"),
        (2, 3),
    )

    path, report = export_kicad_with_report(
        board,
        tmp_path / "buried.kicad_pcb",
    )
    text = path.read_text(encoding="utf-8")
    readback = read_kicad_board_text(text)
    audit = compare_kicad_connectivity(board, readback, report)

    assert "(via buried " in text
    assert len(readback["vias"]) == 1
    assert readback["vias"][0]["type"] == "buried"
    assert readback["vias"][0]["layers"] == ("In1.Cu", "In2.Cu")
    assert report.exported_via_span_ids == ["D1"]
    assert report.skipped_via_span_ids == []
    assert audit["vias"]["equal"] is True
    assert audit["source_equivalent"] is True


def test_x2_blind_kind_mismatch_fails_closed(tmp_path):
    board = _board(
        "blind",
        "In1.Cu",
        "In2.Cu",
        ("In1.Cu", "In2.Cu"),
        (2, 3),
    )

    path, report = export_kicad_with_report(
        board,
        tmp_path / "invalid-blind.kicad_pcb",
    )
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))

    assert readback["vias"] == []
    assert report.exported_via_span_ids == []
    assert report.skipped_via_span_ids == ["D1"]
    assert any(
        issue.code == "KICAD_PROVEN_VIA_KIND_MISMATCH"
        and issue.object_id == "D1"
        for issue in report.issues
    )


def test_x2_buried_kind_mismatch_fails_closed(tmp_path):
    board = _board(
        "buried",
        "F.Cu",
        "In1.Cu",
        ("F.Cu", "In1.Cu"),
        (1, 2),
    )

    path, report = export_kicad_with_report(
        board,
        tmp_path / "invalid-buried.kicad_pcb",
    )
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))

    assert readback["vias"] == []
    assert report.exported_via_span_ids == []
    assert report.skipped_via_span_ids == ["D1"]
    assert any(
        issue.code == "KICAD_PROVEN_VIA_KIND_MISMATCH"
        and issue.object_id == "D1"
        for issue in report.issues
    )


def test_partial_span_without_explicit_x2_type_stays_omitted(tmp_path):
    board = _board(
        None,
        "F.Cu",
        "In1.Cu",
        ("F.Cu", "In1.Cu"),
        None,
    )

    path, report = export_kicad_with_report(
        board,
        tmp_path / "untyped-partial.kicad_pcb",
    )
    readback = read_kicad_board_text(path.read_text(encoding="utf-8"))

    assert readback["vias"] == []
    assert report.skipped_via_span_ids == ["D1"]
    assert any(
        issue.code == "KICAD_PROVEN_VIA_TYPE_UNPROVEN"
        and issue.object_id == "D1"
        for issue in report.issues
    )
