from copy import deepcopy

import pytest

from photonx_eda_pcb.footprints.clustering import (
    cluster_pads,
    cluster_pads_bruteforce,
)
from photonx_eda_pcb.inference.components import (
    infer_component_hypotheses,
    infer_component_hypotheses_bruteforce,
)
from photonx_eda_pcb.models import BoardModel, PadCandidate, Point
from photonx_eda_pcb.spatial_connectivity.native_backend import native_available


def _pads():
    return [
        PadCandidate("A", Point(-2.0, 0.0), 0.5, 0.5, "C", "F.Cu"),
        PadCandidate("B", Point(-1.1, 0.0), 0.5, 0.5, "C", "F.Cu"),
        PadCandidate("C", Point(0.0, 0.0), 0.5, 0.5, "C", "F.Cu"),
        PadCandidate("D", Point(0.0, 0.9), 0.5, 0.5, "C", "F.Cu"),
        PadCandidate("E", Point(8.0, 8.0), 0.5, 0.5, "C", "F.Cu"),
    ]


def _cluster_signature(groups):
    return [[pad.id for pad in group] for group in groups]


def _component_signature(items):
    return [
        (
            item.id,
            tuple(item.pad_ids),
            item.kind,
            item.confidence,
            tuple(item.evidence),
        )
        for item in items
    ]


def test_point_pair_path_preserves_bruteforce_semantics_with_python_backend():
    pads = _pads()
    assert _cluster_signature(cluster_pads_bruteforce(pads, 1.0)) == (
        _cluster_signature(
            cluster_pads(pads, 1.0, spatial_backend="python")
        )
    )

    brute_board = BoardModel(pads=deepcopy(pads))
    spatial_board = BoardModel(pads=deepcopy(pads))
    assert _component_signature(
        infer_component_hypotheses_bruteforce(brute_board, 1.5)
    ) == _component_signature(
        infer_component_hypotheses(
            spatial_board,
            1.5,
            spatial_backend="python",
        )
    )


@pytest.mark.skipif(not native_available(), reason="native C++ library is not built")
def test_cpp_point_pair_consumers_match_python_backend():
    pads = _pads()
    assert _cluster_signature(
        cluster_pads(pads, 1.0, spatial_backend="native")
    ) == _cluster_signature(
        cluster_pads(pads, 1.0, spatial_backend="python")
    )

    native_board = BoardModel(pads=deepcopy(pads))
    python_board = BoardModel(pads=deepcopy(pads))
    assert _component_signature(
        infer_component_hypotheses(
            native_board,
            1.5,
            spatial_backend="native",
        )
    ) == _component_signature(
        infer_component_hypotheses(
            python_board,
            1.5,
            spatial_backend="python",
        )
    )
