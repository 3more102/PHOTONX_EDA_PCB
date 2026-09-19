from copy import deepcopy

import pytest

from photonx_eda_pcb.connectivity.drills import attach_drills, attach_drills_bruteforce
from photonx_eda_pcb.footprints.clustering import cluster_pads, cluster_pads_bruteforce
from photonx_eda_pcb.inference.components import (
    infer_component_hypotheses,
    infer_component_hypotheses_bruteforce,
)
from photonx_eda_pcb.models import BoardModel, DrillHit, PadCandidate, Point


def _pads():
    return [
        PadCandidate("A", Point(0, 0), 0.5, 0.5, "C", "F.Cu"),
        PadCandidate("B", Point(1, 0), 0.5, 0.5, "C", "F.Cu"),
        PadCandidate("C", Point(10, 0), 0.5, 0.5, "C", "F.Cu"),
        PadCandidate("D", Point(11, 0), 0.5, 0.5, "C", "F.Cu"),
    ]


def _component_signature(items):
    return [(x.id, tuple(x.pad_ids), x.kind, x.confidence) for x in items]


def _cluster_signature(groups):
    return [[p.id for p in group] for group in groups]


def test_drill_attachment_can_force_python_backend():
    board = BoardModel(
        pads=[
            PadCandidate("P1", Point(0, 0), 1, 1, "C", "F.Cu"),
            PadCandidate("P2", Point(5, 0), 1, 1, "C", "F.Cu"),
        ],
        drills=[
            DrillHit("D1", Point(0.03, 0), 0.4),
            DrillHit("D2", Point(5.02, 0), 0.6),
        ],
    )
    reference = deepcopy(board)
    assert attach_drills_bruteforce(reference, 0.1) == 2
    assert attach_drills(board, 0.1, backend="python") == 2
    assert [(p.id, p.drill) for p in board.pads] == [
        (p.id, p.drill) for p in reference.pads
    ]


def test_component_inference_can_force_python_backend():
    board = BoardModel(pads=_pads())
    reference = deepcopy(board)
    expected = infer_component_hypotheses_bruteforce(reference, 2)
    actual = infer_component_hypotheses(board, 2, backend="python")
    assert _component_signature(actual) == _component_signature(expected)


def test_footprint_clustering_can_force_python_backend():
    expected = cluster_pads_bruteforce(_pads(), 2)
    actual = cluster_pads(_pads(), 2, backend="python")
    assert _cluster_signature(actual) == _cluster_signature(expected)


@pytest.mark.parametrize(
    "consumer",
    [
        lambda: attach_drills(
            BoardModel(
                pads=[PadCandidate("P", Point(0, 0), 1, 1, "C", "F.Cu")],
                drills=[DrillHit("D", Point(0, 0), 0.4)],
            ),
            backend="gpu",
        ),
        lambda: infer_component_hypotheses(
            BoardModel(pads=_pads()),
            backend="gpu",
        ),
        lambda: cluster_pads(_pads(), backend="gpu"),
    ],
)
def test_spatial_consumers_reject_unknown_backend(consumer):
    with pytest.raises(ValueError, match="backend"):
        consumer()
