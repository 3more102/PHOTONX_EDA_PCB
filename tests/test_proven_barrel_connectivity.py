from photonx_eda_pcb.connectivity import build_physical_graph, assign_physical_nets
from photonx_eda_pcb.connectivity.graph import build_physical_graph_bruteforce
from photonx_eda_pcb.models import BoardModel, DrillHit, PadCandidate, Point


def _pad(pid, layer):
    return PadCandidate(pid, Point(0, 0), 1, 1, "C", layer, 0.4)


def _board(*, plating="plated", span=("F.Cu", "B.Cu"), proven=True):
    return BoardModel(
        pads=[_pad("PF", "F.Cu"), _pad("PB", "B.Cu")],
        drills=[
            DrillHit(
                "D",
                Point(0, 0),
                0.4,
                plating=plating,
                layer_span=span,
                span_proven=proven,
            )
        ],
    )


def test_proven_plated_barrel_connects_layers_and_reconstructed_net():
    board = _board()
    graph = build_physical_graph(board)

    assert graph.has_edge("PF", "PB")
    assert graph["PF"]["PB"]["reason"] == "proven_plated_barrel"
    assert graph["PF"]["PB"]["drill_id"] == "D"
    assert graph["PF"]["PB"]["layer_span"] == ("F.Cu", "B.Cu")

    nets = assign_physical_nets(board, graph)
    assert len(nets) == 1
    assert nets[0].members == ["PB", "PF"]


def test_unknown_non_plated_or_unproven_drill_never_bridges_layers():
    cases = [
        _board(plating="unknown"),
        _board(plating="non-plated"),
        _board(proven=False),
        _board(span=None),
    ]
    for board in cases:
        graph = build_physical_graph(board)
        assert not graph.has_edge("PF", "PB")


def test_explicit_span_does_not_connect_copper_outside_barrel_layers():
    board = BoardModel(
        pads=[
            _pad("PF", "F.Cu"),
            _pad("PI", "In1.Cu"),
            _pad("PB", "B.Cu"),
        ],
        drills=[
            DrillHit(
                "D",
                Point(0, 0),
                0.4,
                plating="plated",
                layer_span=("F.Cu", "In1.Cu"),
                span_proven=True,
            )
        ],
    )

    graph = build_physical_graph(board)
    assert graph.has_edge("PF", "PI")
    assert not graph.has_edge("PF", "PB")
    assert not graph.has_edge("PI", "PB")


def test_barrel_connectivity_spatial_and_bruteforce_paths_match():
    board = _board()
    spatial = build_physical_graph(board)
    brute = build_physical_graph_bruteforce(board)

    assert sorted(spatial.nodes()) == sorted(brute.nodes())
    assert sorted(
        (min(a, b), max(a, b), data["reason"])
        for a, b, data in spatial.edges(data=True)
    ) == sorted(
        (min(a, b), max(a, b), data["reason"])
        for a, b, data in brute.edges(data=True)
    )
