from photonx_eda_pcb.board_variants.model import VariantDefinition,VariantComponent
from photonx_eda_pcb.board_variants.matrix import variant_matrix
def test_variant_matrix():
    a=VariantDefinition("A",{"R1":VariantComponent("R1",False)})
    b=VariantDefinition("B",{"R2":VariantComponent("R2",False)})
    m=variant_matrix([a,b])
    assert m["variants"]["A"]["R1"] is False and m["variants"]["A"]["R2"] is True
