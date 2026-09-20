from pathlib import Path

import pytest

from photonx_eda_pcb.exporters.kicad import export_kicad_with_report
from photonx_eda_pcb.exporters.kicad_policy import proven_via_span_export_plan
from photonx_eda_pcb.kicad_reader import read_kicad_board_text
from photonx_eda_pcb.models import BoardModel, DrillHit, NetGroup, PadCandidate, Point
from photonx_eda_pcb.roundtrip.kicad_connectivity import compare_kicad_connectivity


def _net():
    return NetGroup("N1", [], 1.0, "GND")


def _pad(pad_id: str, layer: str):
    return PadCandidate(
        pad_id,
        Point(0.0, 0.0),
        1.0,
        1.0,
        "C",
        layer,
        None,
        "N1",
    )


def _span(from_layer: str, to_layer: str, *pad_ids: str):
    return {
        "drill_id": "D1",
        "from_layer": from_layer,
        "to_layer": to_layer,
        "confidence": 0.99,
        "proven": True,
        "pad_ids": list(pad_ids),
        "evidence": ["source-proven X2 drill span"],
    }


def _drill(kind: str, layer_span: tuple[str, str], raw_span: tuple[int, int]):
    return DrillHit(
        "D1",
        Point(0.0, 0.0),
        0.4,
        "plated",
        layer_span=layer_span,
        span_proven=True,
        x2_layer_span=raw_span,
        x2_span_kind=kind,
    )


def test_x2_blind_span_exports_as_kicad_blind_via(tmp_path: Path):
    board = BoardModel(
        nets=[_net()],
        pads=[
            _pad("P_F", "F.Cu"),
            _pad("P_I1", "In1.Cu"),
        ],
        drills=[
            _drill("blind", ("F.Cu", "In1.Cu"), (1, 2)),
        ],
        metadata={
            "via_spans": [
                _span("F.Cu", "In1.Cu", "P_F", "P_I1"),
            ]
        },
    )

    path, report = export_kicad_with_report(board, tmp_path / "blind.kicad_pcb")
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


def test_x2_buried_span_serializes_blind_token_and_reads_back_buried(tmp_path: Path):
    board = BoardModel(
        nets=[_net()],
        pads=[
            _pad("P_I1", "In1.Cu"),
            _pad("P_I2", "In2.Cu"),
        ],
        drills=[
            _drill("buried", ("In1.Cu", "In2.Cu"), (2, 3)),
        ],
        metadata={
            "via_spans": [
                _span("In1.Cu", "In2.Cu", "P_I1", "P_I2"),
            ]
        },
    )

    path, report = export_kicad_with_report(board, tmp_path / "buried.kicad_pcb")
    text = path.read_text(encoding="utf-8")
    readback = read_kicad_board_text(text)
    audit = compare_kicad_connectivity(board, readback, report)

    assert "(via blind " in text
    assert "(via buried " not in text
    assert len(readback["vias"]) == 1
    assert readback["vias"][0]["type"] == "buried"
    assert readback["vias"][0]["layers"] == ("In1.Cu", "In2.Cu")
    assert report.exported_via_span_ids == ["D1"]
    assert report.skipped_via_span_ids == []
    assert audit["vias"]["equal"] is True
    assert audit["source_equivalent"] is True


@pytest.mark.parametrize(
    ("kind", "from_layer", "to_layer", "raw_span", "pad_layers"),
    [
        ("blind", "In1.Cu", "In2.Cu", (2, 3), ("In1.Cu", "In2.Cu")),
        ("buried", "F.Cu", "In1.Cu", (1, 2), ("F.Cu", "In1.Cu")),
    ],
)
def test_x2_via_kind_must_match_surface_topology(
    kind,
    from_layer,
    to_layer,
    raw_span,
    pad_layers,
):
    board = BoardModel(
        nets=[_net()],
        pads=[
            _pad("P1", pad_layers[0]),
            _pad("P2", pad_layers[1]),
        ],
        drills=[
            _drill(kind, (from_layer, to_layer), raw_span),
        ],
        metadata={
            "via_spans": [
                _span(from_layer, to_layer, "P1", "P2"),
            ]
        },
    )

    exportable, omitted, problems = proven_via_span_export_plan(board)

    assert exportable == ()
    assert problems == ()
    assert omitted == (
        (
            "D1",
            "KICAD_PROVEN_VIA_X2_KIND_MISMATCH",
            "explicit X2 Blind/Buried kind is inconsistent with the proven canonical layer endpoints",
        ),
    )


def test_x2_partial_via_requires_matching_canonical_proven_span():
    board = BoardModel(
        nets=[_net()],
        pads=[
            _pad("P_F", "F.Cu"),
            _pad("P_I1", "In1.Cu"),
            _pad("P_I2", "In2.Cu"),
        ],
        drills=[
            _drill("blind", ("F.Cu", "In2.Cu"), (1, 3)),
        ],
        metadata={
            "via_spans": [
                _span("F.Cu", "In1.Cu", "P_F", "P_I1"),
            ]
        },
    )

    exportable, omitted, problems = proven_via_span_export_plan(board)

    assert exportable == ()
    assert problems == ()
    assert omitted[0][0:2] == (
        "D1",
        "KICAD_PROVEN_VIA_X2_SPAN_UNPROVEN",
    )


def test_x2_blind_kind_cannot_override_full_stack_through_via():
    board = BoardModel(
        nets=[_net()],
        pads=[
            _pad("P_F", "F.Cu"),
            _pad("P_B", "B.Cu"),
        ],
        drills=[
            _drill("blind", ("F.Cu", "B.Cu"), (1, 2)),
        ],
        metadata={
            "via_spans": [
                _span("F.Cu", "B.Cu", "P_F", "P_B"),
            ]
        },
    )

    exportable, omitted, problems = proven_via_span_export_plan(board)

    assert exportable == ()
    assert problems == ()
    assert omitted[0][0:2] == (
        "D1",
        "KICAD_PROVEN_VIA_X2_KIND_MISMATCH",
    )
