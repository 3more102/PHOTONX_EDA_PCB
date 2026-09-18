from photonx_eda_pcb.models import BoardModel,PadCandidate,Point
from photonx_eda_pcb.mechanical_features import SlotFeature
from photonx_eda_pcb.drc import run_drc
from photonx_eda_pcb.drc.model import DrcConfig

def _board(plating,pad_y=.8):
    p=PadCandidate("P",Point(2,pad_y),.5,.5,"C","F.Cu")
    s=SlotFeature("S",(0,0),(4,0),1.0,plating)
    return BoardModel(pads=[p],slots=[s])

def test_unknown_slot_clearance_is_warning():
    issues=[x for x in run_drc(_board("unknown"),DrcConfig()) if x.code=="MECHANICAL_COPPER_CLEARANCE"]
    assert issues and all(x.severity=="warning" for x in issues)

def test_nonplated_slot_clearance_is_error():
    issues=[x for x in run_drc(_board("non-plated"),DrcConfig()) if x.code=="MECHANICAL_COPPER_CLEARANCE"]
    assert issues and all(x.severity=="error" for x in issues)

def test_plated_slot_is_not_forced_to_mechanical_clearance_error():
    assert not [x for x in run_drc(_board("plated"),DrcConfig()) if x.code=="MECHANICAL_COPPER_CLEARANCE"]

def test_slot_above_clearance_limit_is_not_reported():
    assert not [x for x in run_drc(_board("non-plated",1.0),DrcConfig()) if x.code=="MECHANICAL_COPPER_CLEARANCE"]
