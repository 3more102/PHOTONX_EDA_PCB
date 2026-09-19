from copy import deepcopy

from photonx_eda_pcb.inference.components import (
    infer_component_hypotheses,
    infer_component_hypotheses_bruteforce,
)
from photonx_eda_pcb.models import BoardModel,PadCandidate,Point
from photonx_eda_pcb.provenance import Evidence,Provenance


def _pad(pid,x,refdes_values):
    provenance=Provenance()
    for refdes in refdes_values:
        provenance.add_evidence(
            Evidence("gerber_x2_component_refdes",refdes,1.0)
        )
    return PadCandidate(pid,Point(x,0.0),0.5,0.5,"C","F.Cu",provenance=provenance)


def _signature(items):
    return [
        (
            item.id,
            tuple(item.pad_ids),
            item.kind,
            item.confidence,
            tuple(item.evidence),
            item.reference,
        )
        for item in items
    ]


def test_x2_refdes_groups_multi_pad_component_before_geometric_pairing():
    board=BoardModel(
        pads=[
            _pad("P1",0.0,["U1"]),
            _pad("P2",0.8,["U1"]),
            _pad("P3",1.6,["U1"]),
            _pad("P4",2.4,["U1"]),
        ]
    )

    components=infer_component_hypotheses(board,1.0,backend="python")

    assert len(components)==1
    component=components[0]
    assert component.pad_ids==["P1","P2","P3","P4"]
    assert component.kind=="x2_component_candidate"
    assert component.reference=="U1"
    assert component.confidence==1.0
    assert any("Gerber X2 TO.P identifies reference U1"==item for item in component.evidence)


def test_disconnected_repeated_x2_refdes_fails_closed_to_geometry():
    board=BoardModel(
        pads=[
            _pad("P1",0.0,["U1"]),
            _pad("P2",0.8,["U1"]),
            _pad("P3",20.0,["U1"]),
            _pad("P4",20.8,["U1"]),
        ]
    )

    components=infer_component_hypotheses(board,1.0,backend="python")

    assert len(components)==2
    assert all(component.reference is None for component in components)
    assert {tuple(component.pad_ids) for component in components}=={
        ("P1","P2"),
        ("P3","P4"),
    }


def test_ambiguous_x2_refdes_taints_source_promotion():
    board=BoardModel(
        pads=[
            _pad("P1",0.0,["U1","U2"]),
            _pad("P2",0.8,["U1"]),
        ]
    )

    components=infer_component_hypotheses(board,1.0,backend="python")

    assert len(components)==1
    assert components[0].reference is None
    assert components[0].pad_ids==["P1","P2"]


def test_x2_component_inference_keeps_spatial_and_bruteforce_parity():
    board=BoardModel(
        pads=[
            _pad("P1",0.0,["U1"]),
            _pad("P2",0.8,["U1"]),
            _pad("P3",1.6,["U1"]),
            _pad("Q1",10.0,[]),
            _pad("Q2",10.8,[]),
        ]
    )
    reference=deepcopy(board)

    expected=infer_component_hypotheses_bruteforce(reference,1.0)
    actual=infer_component_hypotheses(board,1.0,backend="python")

    assert _signature(actual)==_signature(expected)
