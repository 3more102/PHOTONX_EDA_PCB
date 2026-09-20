from types import SimpleNamespace as NS

import pytest

from photonx_eda_pcb.connectivity.graph import (
    build_physical_graph,
    build_physical_graph_bruteforce,
)
from photonx_eda_pcb.connectivity.nets import assign_physical_nets
from photonx_eda_pcb.copper_solver.layer_rules import vertical_connection_allowed
from photonx_eda_pcb.models import BoardModel, DrillHit, PadCandidate, Point
from photonx_eda_pcb.pipeline import _report_unproven_multilayer_spans
from photonx_eda_pcb.stackup import infer_stackup
from photonx_eda_pcb.via_span import resolve_via_spans


def _board(plating="plated"):
    return BoardModel(
        pads=[
            PadCandidate(
                "P_F",
                Point(10.0, 10.0),
                1.0,
                1.0,
                "C",
                "F.Cu",
            ),
            PadCandidate(
                "P_B",
                Point(10.0, 10.0),
                1.0,
                1.0,
                "C",
                "B.Cu",
            ),
        ],
        drills=[
            DrillHit(
                "D1",
                Point(10.0, 10.0),
                0.4,
                plating,
            )
        ],
    )


def _spans(board):
    return resolve_via_spans(
        board,
        infer_stackup(board),
        tolerance_mm=0.15,
    )


def _edges(graph):
    return sorted(
        (min(left, right), max(left, right), data.get("reason"))
        for left, right, data in graph.edges(data=True)
    )


def test_proven_plated_via_bridges_front_and_back_copper():
    board = _board("plated")
    spans = _spans(board)

    assert len(spans) == 1
    assert spans[0].proven is True
    assert spans[0].from_layer == "F.Cu"
    assert spans[0].to_layer == "B.Cu"
    assert spans[0].pad_ids == ("P_B", "P_F")

    graph = build_physical_graph(board, via_spans=spans)
    brute = build_physical_graph_bruteforce(board, via_spans=spans)

    assert _edges(graph) == _edges(brute)
    assert graph.has_edge("P_F", "P_B")
    edge = graph["P_F"]["P_B"]
    assert edge["reason"] == "plated_via_span"
    assert edge["drill_id"] == "D1"
    assert edge["from_layer"] == "F.Cu"
    assert edge["to_layer"] == "B.Cu"
    assert edge["confidence"] == pytest.approx(0.95)

    nets = assign_physical_nets(board, graph)
    assert len(nets) == 1
    assert set(nets[0].members) == {"P_F", "P_B"}
    assert nets[0].confidence == pytest.approx(0.95)
    assert any(
        item.kind == "plated_via_span"
        and "drill=D1" in item.detail
        for item in nets[0].provenance.evidence
    )


@pytest.mark.parametrize("plating", ["unknown", "non-plated"])
def test_unproven_or_nonplated_hole_never_bridges_layers(plating):
    board = _board(plating)
    spans = _spans(board)

    assert spans[0].proven is False

    graph = build_physical_graph(board, via_spans=spans)
    assert graph.has_edge("P_F", "P_B") is False

    nets = assign_physical_nets(board, graph)
    assert len(nets) == 2


def test_unknown_multilayer_plating_is_fail_visible():
    board = _board("unknown")
    board.metadata["source_input"] = "fixture"
    spans = _spans(board)

    _report_unproven_multilayer_spans(board, spans)

    issues = [
        item
        for item in board.diagnostics
        if item.code == "MULTILAYER_SPAN_UNKNOWN"
    ]
    assert len(issues) == 1
    assert issues[0].severity == "warning"
    assert "no vertical electrical connection was created" in issues[0].message


def test_explicit_nonplated_multilayer_overlap_is_not_reported_as_unknown():
    board = _board("non-plated")
    board.metadata["source_input"] = "fixture"
    spans = _spans(board)

    _report_unproven_multilayer_spans(board, spans)

    assert not [
        item
        for item in board.diagnostics
        if item.code == "MULTILAYER_SPAN_UNKNOWN"
    ]


def test_vertical_contact_requires_both_plating_and_proven_span():
    assert vertical_connection_allowed(
        NS(plating="plated", span_proven=True)
    )
    assert not vertical_connection_allowed(
        NS(plating="plated", span_proven=False)
    )
    assert not vertical_connection_allowed(
        NS(plating="unknown", span_proven=True)
    )
