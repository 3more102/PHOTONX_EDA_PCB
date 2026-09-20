from math import cos,radians,sin
from types import SimpleNamespace

import pytest

from photonx_eda_pcb.footprints.infer import infer_footprints
from photonx_eda_pcb.footprints.matcher import match_signature
from photonx_eda_pcb.models import PadCandidate,Point


def _pad(pid,x,y,*,drill=None,size=(0.6,1.2),shape="R"):
    return PadCandidate(pid,Point(x,y),size[0],size[1],shape,"F.Cu",drill=drill)


def _rotate(x,y,angle_deg):
    angle=radians(angle_deg)
    return (
        x*cos(angle)-y*sin(angle),
        x*sin(angle)+y*cos(angle),
    )


def _dual_row_8(*,angle_deg=0.0,drill=None):
    pads=[]
    index=1
    for x in (-3.0,3.0):
        for y in (-1.905,-0.635,0.635,1.905):
            xr,yr=_rotate(x,y,angle_deg)
            pads.append(_pad(f"P{index}",xr,yr,drill=drill))
            index+=1
    return pads


@pytest.mark.parametrize("angle_deg",[0.0,17.0,37.0,90.0,133.0])
def test_soic8_signature_is_rotation_invariant(angle_deg):
    match=match_signature(_dual_row_8(angle_deg=angle_deg))
    assert match["best"]=="SOIC8_LIKE"
    assert match["confidence"]>=0.95
    assert match["features"]["primary_group_sizes"]==(4,4)
    assert match["features"]["secondary_group_sizes"]==(2,2,2,2)


def test_dip8_signature_requires_drill_evidence_but_not_plating_inference():
    match=match_signature(_dual_row_8(angle_deg=31.0,drill=0.8))
    assert match["best"]=="DIP8_LIKE"
    assert match["confidence"]>=0.95


def test_irregular_eight_pad_cloud_is_not_promoted_to_dual_row_package():
    pads=[
        _pad("P1",0.0,0.0),
        _pad("P2",0.9,0.2),
        _pad("P3",2.1,-0.1),
        _pad("P4",3.8,0.4),
        _pad("P5",0.1,2.0),
        _pad("P6",1.5,2.7),
        _pad("P7",3.0,1.8),
        _pad("P8",4.2,3.1),
    ]
    match=match_signature(pads)
    assert match["best"] is None
    assert match["confidence"]==0.0


def test_matcher_fails_closed_when_top_signatures_are_tied():
    pads=[_pad("A",-1.0,0.0,size=(1.0,1.0)),_pad("B",1.0,0.0,size=(1.0,1.0))]
    signatures=[
        {"name":"ALPHA","pad_count":2,"drilled_max":0.1,"aspect_min":1.2,"pad_area_cv_max":0.35},
        {"name":"BETA","pad_count":2,"drilled_max":0.1,"aspect_min":1.2,"pad_area_cv_max":0.35},
    ]
    match=match_signature(pads,signatures=signatures)
    assert match["best"] is None
    assert match["ambiguous"] is True
    assert match["confidence"]==0.0
    assert match["margin"]==pytest.approx(0.0)


def test_inference_preserves_geometry_hypothesis_evidence():
    board=SimpleNamespace(pads=_dual_row_8(angle_deg=23.0))
    candidate=infer_footprints(board,max_gap_mm=6.1,max_cluster_span_mm=7.5)[0]
    assert candidate.signature=="SOIC8_LIKE"
    assert candidate.confidence>=0.95
    assert any("geometry signature SOIC8_LIKE accepted" in item for item in candidate.evidence)


def test_two_pad_smd_behavior_remains_supported():
    match=match_signature([
        _pad("A",-1.0,0.0,size=(1.0,1.0)),
        _pad("B",1.0,0.0,size=(1.0,1.0)),
    ])
    assert match["best"]=="TWO_PAD_SMD"
    assert match["confidence"]>=0.65
