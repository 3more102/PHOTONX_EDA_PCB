from photonx_eda_pcb.board_variants.model import VariantDefinition,VariantComponent
from photonx_eda_pcb.pick_place.model import Placement
from photonx_eda_pcb.variant_reconciliation.placements import reconcile_variant_placements
def test_variant_placement_ignores_dnp():
    v=VariantDefinition("lite",{"R1":VariantComponent("R1",False)})
    a=[Placement("R1",0,0),Placement("R2",1,0)];b=[Placement("R2",1,0)]
    out=reconcile_variant_placements(a,b,v)
    assert len(out)==1 and out[0].reference=="R2" and out[0].code=="OK"
