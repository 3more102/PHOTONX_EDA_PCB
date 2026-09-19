from types import SimpleNamespace

import pytest

from photonx_eda_pcb.footprints.clustering import cluster_pads,cluster_pads_bruteforce
from photonx_eda_pcb.footprints.infer import infer_footprints
from photonx_eda_pcb.models import PadCandidate,Point


def _pad(pid,x,y):
    return PadCandidate(pid,Point(x,y),0.5,0.5,"C","F.Cu")


def _pads():
    return [_pad("A",0,0),_pad("B",1,0),_pad("C",2,0),_pad("D",10,0)]


def _signature(groups):
    return [[pad.id for pad in group] for group in groups]


def test_default_clustering_preserves_existing_single_linkage_semantics():
    assert _signature(cluster_pads(_pads(),1.1))==[["A","B","C"],["D"]]


def test_span_guard_splits_transitive_pad_bridge_with_reference_parity():
    expected=[["A","B"],["C"],["D"]]
    assert _signature(cluster_pads(_pads(),1.1,max_cluster_span_mm=1.1))==expected
    assert _signature(cluster_pads_bruteforce(_pads(),1.1,max_cluster_span_mm=1.1))==expected


def test_span_guard_repartitions_buckets_that_lose_their_max_gap_bridge():
    pads=[
        _pad("A",0,6),
        _pad("B",1,3),
        _pad("C",0,2),
        _pad("D",3,5),
        _pad("E",1,5),
    ]
    expected=[["A"],["B","C"],["D","E"]]
    assert _signature(cluster_pads(pads,2.1,max_cluster_span_mm=4.0))==expected
    assert _signature(cluster_pads_bruteforce(pads,2.1,max_cluster_span_mm=4.0))==expected


def test_span_guard_is_exposed_through_footprint_inference():
    board=SimpleNamespace(pads=_pads()[:3])
    assert [item.pad_ids for item in infer_footprints(board,1.1,max_cluster_span_mm=1.1)]==[["A","B"],["C"]]


@pytest.mark.parametrize("value",[0,-1,float("inf"),float("nan")])
def test_span_guard_rejects_invalid_limits(value):
    with pytest.raises(ValueError,match="positive finite"):
        cluster_pads(_pads(),1.1,max_cluster_span_mm=value)
