from pathlib import Path

import pytest

from photonx_eda_pcb.models import BoardModel, DrillHit, PadCandidate, Point
from photonx_eda_pcb.parsers.manifest import infer_drill_plating_hint
from photonx_eda_pcb.pipeline import reconstruct
from photonx_eda_pcb.stackup import infer_stackup
from photonx_eda_pcb.via_span import resolve_via_spans
from photonx_eda_pcb.via_span.candidates import (
    pads_near_drill,
    pads_near_drill_bruteforce,
)


GERBER_FLASH = """%FSLAX24Y24*%
%MOMM*%
%ADD10C,1.000*%
D10*
X010000Y010000D03*
M02*
"""

EXCELLON_HIT = """M48
METRIC
T01C0.400
%
T01
X1.000Y1.000
M30
"""


@pytest.mark.parametrize(
    ("filename", "expected"),
    [
        ("board-PTH.drl", "plated"),
        ("board_pth.xln", "plated"),
        ("board-plated.drl", "plated"),
        ("board-NPTH.drl", "non-plated"),
        ("board_non-plated.drl", "non-plated"),
        ("board-unplated.xnc", "non-plated"),
        ("board_drill.drl", None),
        ("depth.drl", None),
    ],
)
def test_explicit_drill_filename_tokens_are_conservative(filename, expected):
    assert infer_drill_plating_hint(filename) == expected


@pytest.mark.parametrize(
    ("drill_name", "expected_plating", "expected_nets", "expected_proven"),
    [
        ("board-PTH.drl", "plated", 1, True),
        ("board-NPTH.drl", "non-plated", 2, False),
        ("board.drl", "unknown", 2, False),
    ],
)
def test_normal_pipeline_applies_plating_evidence_before_via_resolution(
    tmp_path: Path,
    drill_name: str,
    expected_plating: str,
    expected_nets: int,
    expected_proven: bool,
):
    (tmp_path / "top.gtl").write_text(GERBER_FLASH, encoding="utf-8")
    (tmp_path / "bottom.gbl").write_text(GERBER_FLASH, encoding="utf-8")
    (tmp_path / drill_name).write_text(EXCELLON_HIT, encoding="utf-8")

    result = reconstruct(tmp_path)
    board = result.board

    assert len(board.pads) == 2
    assert len(board.drills) == 1
    assert board.drills[0].plating == expected_plating
    assert len(board.nets) == expected_nets

    spans = board.metadata["via_spans"]
    assert len(spans) == 1
    assert spans[0]["proven"] is expected_proven

    if expected_plating == "unknown":
        assert "drill_plating_evidence" not in board.metadata
        assert any(
            item.code == "MULTILAYER_SPAN_UNKNOWN"
            for item in board.diagnostics
        )
    else:
        evidence = board.metadata["drill_plating_evidence"]
        assert len(evidence) == 1
        assert evidence[0]["plating"] == expected_plating
        assert evidence[0]["source"] == "explicit_filename_token"


def _elongated_pad_board(drill_y: float) -> BoardModel:
    return BoardModel(
        pads=[
            PadCandidate(
                "P_F",
                Point(0.0, 0.0),
                2.0,
                0.4,
                "R",
                "F.Cu",
            ),
            PadCandidate(
                "P_B",
                Point(0.0, 0.0),
                2.0,
                0.4,
                "R",
                "B.Cu",
            ),
        ],
        drills=[
            DrillHit(
                "D1",
                Point(0.0, drill_y),
                0.2,
                "plated",
            )
        ],
    )


def test_elongated_pad_proximity_does_not_fake_a_via_span():
    board = _elongated_pad_board(0.8)
    drill = board.drills[0]

    spatial = pads_near_drill(board, drill, tolerance_mm=0.03)
    brute = pads_near_drill_bruteforce(board, drill, tolerance_mm=0.03)
    assert spatial == brute == []

    spans = resolve_via_spans(
        board,
        infer_stackup(board),
        tolerance_mm=0.03,
    )
    assert len(spans) == 1
    assert spans[0].pad_ids == ()
    assert spans[0].proven is False
    assert spans[0].from_layer is None
    assert spans[0].to_layer is None


def test_shape_accurate_contact_still_proves_real_rectangular_via_span():
    board = _elongated_pad_board(0.1)
    drill = board.drills[0]

    spatial = pads_near_drill(board, drill, tolerance_mm=0.03)
    brute = pads_near_drill_bruteforce(board, drill, tolerance_mm=0.03)
    assert [pad.id for pad in spatial] == ["P_B", "P_F"]
    assert [pad.id for pad in brute] == ["P_B", "P_F"]

    spans = resolve_via_spans(
        board,
        infer_stackup(board),
        tolerance_mm=0.03,
    )
    assert len(spans) == 1
    assert spans[0].pad_ids == ("P_B", "P_F")
    assert spans[0].proven is True
    assert spans[0].from_layer == "F.Cu"
    assert spans[0].to_layer == "B.Cu"
