from photonx_eda_pcb.pick_place.model import Placement
from photonx_eda_pcb.placement_reconciliation import reconcile_placements,validate_placement_deltas
def test_placement_reconciliation():
    a=[Placement("U1",0,0,0,"top")];b=[Placement("U1",0.1,0,3,"top")]
    d=reconcile_placements(a,b,.25,5)
    assert d[0].code=="OK" and validate_placement_deltas(d)==[]
