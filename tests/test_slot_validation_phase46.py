from photonx_eda_pcb.models import BoardModel
from photonx_eda_pcb.mechanical_features import SlotFeature
from photonx_eda_pcb.validation import validate_board

def test_invalid_slot_width_is_core_error():
    r=validate_board(BoardModel(slots=[SlotFeature("S",(0,0),(1,0),0,"unknown")]))
    assert any(x.code=="SLOT_WIDTH_INVALID" for x in r.errors)

def test_zero_length_slot_is_warning():
    r=validate_board(BoardModel(slots=[SlotFeature("S",(0,0),(0,0),.5,"unknown")]))
    assert any(x.code=="SLOT_ZERO_LENGTH" for x in r.warnings)

def test_non_finite_slot_width_is_core_error():
    for width in (float("nan"),float("inf"),float("-inf")):
        r=validate_board(BoardModel(slots=[SlotFeature("S",(0,0),(1,0),width,"unknown")]))
        assert any(x.code=="SLOT_WIDTH_INVALID" for x in r.errors)

def test_non_finite_slot_coordinates_are_core_error():
    cases=(
        ((float("nan"),0),(1,0)),
        ((0,float("inf")),(1,0)),
        ((0,0),(float("-inf"),0)),
    )
    for start,end in cases:
        r=validate_board(BoardModel(slots=[SlotFeature("S",start,end,.5,"unknown")]))
        assert any(x.code=="SLOT_COORDINATE_INVALID" for x in r.errors)
