import pytest

from photonx_eda_pcb.models import BoardModel, DrillHit, PadCandidate, Point
from photonx_eda_pcb.spatial_connectivity.native_backend import native_available
from photonx_eda_pcb.stackup.model import LayerSpec, StackupModel
from photonx_eda_pcb.via_span.candidates import (
    build_pad_candidate_index,
    pads_near_drill_bruteforce,
    pads_near_drills,
)
from photonx_eda_pcb.via_span.resolve import resolve_via_spans


def _board():
    return BoardModel(
        pads=[
            PadCandidate("F0", Point(0.0, 0.0), 2.0, 2.0, "C", "F.Cu"),
            PadCandidate("B0", Point(0.0, 0.0), 2.0, 2.0, "C", "B.Cu"),
            PadCandidate("F5", Point(5.0, 0.0), 0.5, 0.5, "C", "F.Cu"),
            PadCandidate("B5", Point(5.0, 0.0), 0.5, 0.5, "C", "B.Cu"),
        ],
        drills=[
            DrillHit("D0", Point(0.5, 0.0), 0.4, "plated"),
            DrillHit("D-corner", Point(0.9, 0.9), 0.4, "plated"),
            DrillHit("D5", Point(5.08, 0.0), 0.3, "plated"),
        ],
    )


def _stackup():
    return StackupModel(
        [
            LayerSpec("F.Cu", "top", 0, True),
            LayerSpec("B.Cu", "bottom", 1, True),
        ]
    )


def _ids(groups):
    return [[p.id for p in group] for group in groups]


def test_batched_via_candidates_match_per_drill_reference_with_variable_pad_sizes():
    board = _board()
    index, by_id = build_pad_candidate_index(board, 0.15)
    expected = [
        pads_near_drill_bruteforce(board, drill, 0.15)
        for drill in board.drills
    ]
    actual = pads_near_drills(
        board,
        board.drills,
        0.15,
        index=index,
        pad_by_id=by_id,
        spatial_backend="python",
    )

    assert _ids(actual) == _ids(expected)
    assert _ids(actual)[1] == []


@pytest.mark.skipif(not native_available(), reason="native C++ library is not built")
def test_native_batched_via_candidates_match_python_and_bruteforce():
    board = _board()
    index, by_id = build_pad_candidate_index(board, 0.15)

    native = pads_near_drills(
        board,
        board.drills,
        0.15,
        index=index,
        pad_by_id=by_id,
        spatial_backend="native",
    )
    python = pads_near_drills(
        board,
        board.drills,
        0.15,
        index=index,
        pad_by_id=by_id,
        spatial_backend="python",
    )
    brute = [
        pads_near_drill_bruteforce(board, drill, 0.15)
        for drill in board.drills
    ]

    assert _ids(native) == _ids(python) == _ids(brute)


@pytest.mark.skipif(not native_available(), reason="native C++ library is not built")
def test_native_via_span_resolution_matches_bruteforce():
    board = _board()
    stackup = _stackup()

    brute = resolve_via_spans(
        board,
        stackup,
        0.15,
        use_spatial_index=False,
    )
    native = resolve_via_spans(
        board,
        stackup,
        0.15,
        spatial_backend="native",
    )

    def signature(items):
        return [
            (x.drill_id, x.from_layer, x.to_layer, x.confidence, x.proven)
            for x in items
        ]

    assert signature(native) == signature(brute)
