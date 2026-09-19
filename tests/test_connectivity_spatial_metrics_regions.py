from photonx_eda_pcb.connectivity.graph import build_physical_graph
from photonx_eda_pcb.connectivity.spatial_metrics import connectivity_candidate_metrics
from photonx_eda_pcb.models import BoardModel, CopperRegion, PadCandidate, Point, Track


def test_connectivity_metrics_use_same_copper_object_universe_as_graph():
    board = BoardModel(
        tracks=[
            Track(
                "T1",
                Point(0.0, 0.0),
                Point(1.0, 0.0),
                0.2,
                "F.Cu",
            )
        ],
        pads=[
            PadCandidate(
                "P1",
                Point(10.0, 0.0),
                1.0,
                1.0,
                "rect",
                "F.Cu",
            )
        ],
        regions=[
            CopperRegion(
                "R1",
                (
                    Point(20.0, 0.0),
                    Point(21.0, 0.0),
                    Point(21.0, 1.0),
                    Point(20.0, 1.0),
                    Point(20.0, 0.0),
                ),
                "F.Cu",
            )
        ],
    )

    graph = build_physical_graph(board)
    metrics = connectivity_candidate_metrics(board)

    assert graph.number_of_nodes() == 3
    assert metrics["objects"] == graph.number_of_nodes()
    assert metrics["same_layer_bruteforce_pairs"] == 3
    assert metrics["spatial_candidate_pairs"] == 0
    assert metrics["reduction_ratio"] == 1.0
