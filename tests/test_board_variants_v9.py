from photonx_eda_pcb.board_variants import VariantDefinition,VariantComponent,apply_variant,validate_variant
from photonx_eda_pcb.pick_place.model import Placement
def test_variant_dnp():
    v=VariantDefinition("lite",{"R1":VariantComponent("R1",False)})
    fitted,dnp=apply_variant([Placement("R1",0,0),Placement("R2",1,0)],v)
    assert [x.reference for x in fitted]==["R2"] and [x.reference for x in dnp]==["R1"]
    assert validate_variant(v)==[]
