from types import SimpleNamespace as NS

import pytest

from photonx_eda_pcb.connectivity.graph import (
    build_physical_graph,
    build_physical_graph_bruteforce,
)
from photonx_eda_pcb.connectivity.nets import assign_physical_nets
from photonx_eda_pcb.copper_solver.layer_rules import vertical_connection_allowed
from photonx_eda_pcb.models import (
    BoardModel,
    CopperRegion,
    DrillHit,
    PadCandidate,
    Point,
    Track,
)
from photonx_eda_pcb.pipeline import (
    _report_unproven_multilayer_spans,
    _serialize_via_spans,
)
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


def test_copper_inside_finished_hole_without_wall_contact_stays_disconnected():
    board = _board("plated")
    board.tracks.append(
        Track(
            "T_INNER",
            Point(10.0, 10.0),
            Point(10.05, 10.0),
            0.04,
            "In1.Cu",
        )
    )
    spans = _spans(board)

    assert spans[0].layer_ids == ("F.Cu", "In1.Cu", "B.Cu")

    graph = build_physical_graph(board, via_spans=spans)

    assert graph.has_edge("P_F", "P_B")
    assert graph.degree["T_INNER"] == 0
    nets = assign_physical_nets(board, graph)
    assert len(nets) == 2


def test_injected_proven_span_cannot_override_unknown_source_plating():
    board = _board("unknown")
    fake_span = NS(
        drill_id="D1",
        from_layer="F.Cu",
        to_layer="B.Cu",
        confidence=0.99,
        evidence=("injected",),
        proven=True,
        pad_ids=("P_B", "P_F"),
        layer_ids=("F.Cu", "B.Cu"),
    )

    graph = build_physical_graph(board, via_spans=[fake_span])

    assert not graph.has_edge("P_F", "P_B")


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


def test_proven_plated_via_barrel_connects_touching_inner_layer_copper():
    board = _board("plated")
    board.tracks.append(
        Track(
            "T_I1",
            Point(9.7, 10.0),
            Point(10.3, 10.0),
            0.12,
            "In1.Cu",
        )
    )
    board.regions.append(
        CopperRegion(
            "R_I2",
            (
                Point(9.8, 9.8),
                Point(10.2, 9.8),
                Point(10.2, 10.2),
                Point(9.8, 10.2),
            ),
            "In2.Cu",
        )
    )
    spans = _spans(board)

    assert spans[0].proven is True
    assert spans[0].layer_ids == ("F.Cu", "In1.Cu", "In2.Cu", "B.Cu")

    graph = build_physical_graph(board, via_spans=spans)
    brute = build_physical_graph_bruteforce(board, via_spans=spans)

    assert _edges(graph) == _edges(brute)
    assert graph.has_edge("P_F", "T_I1")
    assert graph.has_edge("T_I1", "R_I2")
    assert graph.has_edge("R_I2", "P_B")
    assert graph["P_F"]["T_I1"]["contact"] == "barrel_touch"

    nets = assign_physical_nets(board, graph)
    assert len(nets) == 1
    assert set(nets[0].members) == {"P_F", "P_B", "T_I1", "R_I2"}
    via_evidence = [
        item
        for item in nets[0].provenance.evidence
        if item.kind == "plated_via_span"
    ]
    assert len(via_evidence) == 1
    assert "pads=P_B,P_F" in via_evidence[0].detail
    assert "barrel_contacts=R_I2,T_I1" in via_evidence[0].detail

    serialized = _serialize_via_spans(spans)
    assert serialized[0]["layer_ids"] == ["F.Cu", "In1.Cu", "In2.Cu", "B.Cu"]


def test_unproven_via_never_connects_touching_inner_layer_copper():
    board = _board("unknown")
    board.tracks.append(
        Track(
            "T_I1",
            Point(9.7, 10.0),
            Point(10.3, 10.0),
            0.12,
            "In1.Cu",
        )
    )
    spans = _spans(board)

    assert spans[0].proven is False

    graph = build_physical_graph(board, via_spans=spans)
    assert graph.has_edge("P_F", "T_I1") is False
    assert graph.has_edge("P_B", "T_I1") is False
