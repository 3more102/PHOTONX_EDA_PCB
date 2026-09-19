from types import SimpleNamespace

import pytest

from photonx_eda_pcb.footprints.clustering import cluster_pads,cluster_pads_bruteforce
from photonx_eda_pcb.footprints.infer import infer_footprints
from photonx_eda_pcb.models import PadCandidate,Point


def _pads():
    return [
        PadCandidate("A",Point(0,0),0.5,0.5,"C","F.Cu"),
        PadCandidate("B",Point(1,0),0.5,0.5,"C","F.Cu"),
        PadCandidate("C",Point(2,0),0.5,0.5,"C","F.Cu"),
        PadCandidate("D",Point(10,0),0.5,0.5,"C","F.Cu"),
    ]


def _signature(groups):
    return [[pad.id for pad in group] for group in groups]


def test_default_clustering_preserves_existing_single_linkage_semantics():
    assert _signature(cluster_pads(_pads(),1.1))==[["A","B","C"],["D"]]


def test_span_guard_splits_transitive_pad_bridge_with_reference_parity():
    expected=[["A","B"],["C"],["D"]]
    assert _signature(cluster_pads(_pads(),1.1,max_cluster_span_mm=1.1))==expected
    assert _signature(cluster_pads_bruteforce(_pads(),1.1,max_cluster_span_mm=1.1))==expected


def test_span_guard_is_exposed_through_footprint_inference():
    board=SimpleNamespace(pads=_pads()[:3])
    assert [item.pad_ids for item in infer_footprints(board,1.1,max_cluster_span_mm=1.1)]==[["A","B"],["C"]]


@pytest.mark.parametrize("value",[0,-1,float("inf"),float("nan")])
def test_span_guard_rejects_invalid_limits(value):
    with pytest.raises(ValueError,match="positive finite"):
        cluster_pads(_pads(),1.1,max_cluster_span_mm=value)
