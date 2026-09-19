from photonx_eda_pcb.models import BoardModel,DrillHit,PadCandidate,Point
from photonx_eda_pcb.stackup.model import LayerSpec,StackupModel
from photonx_eda_pcb.via_span import resolve_via_spans


def _stack4():
    return StackupModel([
        LayerSpec("F.Cu","top",0,True),
        LayerSpec("In1.Cu","inner",1,True),
        LayerSpec("In2.Cu","inner",2,True),
        LayerSpec("B.Cu","bottom",3,True),
    ])


def _pad(pid,layer):
    return PadCandidate(pid,Point(0,0),1,1,"C",layer)


def test_plating_and_xy_overlap_do_not_prove_layer_span():
    board=BoardModel(
        pads=[_pad("F","F.Cu"),_pad("B","B.Cu")],
        drills=[DrillHit("D",Point(0,0),.4,"plated")],
    )
    span=resolve_via_spans(board,_stack4())[0]
    assert (span.from_layer,span.to_layer)==("F.Cu","B.Cu")
    assert not span.proven
    assert "observed multi-layer pad overlap is span hypothesis only" in span.evidence


def test_explicit_proven_span_is_normalized_to_stackup_order():
    drill=DrillHit("D",Point(0,0),.4,"plated")
    drill.layer_span=("B.Cu","In1.Cu")
    drill.span_proven=True
    board=BoardModel(pads=[_pad("I","In1.Cu"),_pad("B","B.Cu")],drills=[drill])
    span=resolve_via_spans(board,_stack4())[0]
    assert (span.from_layer,span.to_layer)==("In1.Cu","B.Cu")
    assert span.proven
    assert span.confidence==0.99


def test_invalid_explicit_span_fails_closed_without_overlap_fallback():
    drill=DrillHit("D",Point(0,0),.4,"plated")
    drill.layer_span=("F.Cu","In9.Cu")
    drill.span_proven=True
    board=BoardModel(pads=[_pad("F","F.Cu"),_pad("B","B.Cu")],drills=[drill])
    span=resolve_via_spans(board,_stack4())[0]
    assert (span.from_layer,span.to_layer)==(None,None)
    assert not span.proven
    assert any("explicit layer span rejected" in item for item in span.evidence)


def test_observed_layer_outside_explicit_span_blocks_proven_state():
    drill=DrillHit("D",Point(0,0),.4,"plated")
    drill.layer_span=("F.Cu","In1.Cu")
    drill.span_proven=True
    board=BoardModel(
        pads=[_pad("F","F.Cu"),_pad("I1","In1.Cu"),_pad("B","B.Cu")],
        drills=[drill],
    )
    span=resolve_via_spans(board,_stack4())[0]
    assert (span.from_layer,span.to_layer)==("F.Cu","In1.Cu")
    assert not span.proven
    assert span.confidence==0.2
    assert any("conflicts with observed pad layer" in item for item in span.evidence)
