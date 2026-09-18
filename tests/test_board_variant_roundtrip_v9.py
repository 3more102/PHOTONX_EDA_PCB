from photonx_eda_pcb.board_variants.model import VariantDefinition,VariantComponent
from photonx_eda_pcb.board_variants.serialize import dumps_variant,loads_variant
def test_variant_roundtrip():
    v=VariantDefinition("A",{"C1":VariantComponent("C1",True,"100n","C_0603")})
    assert loads_variant(dumps_variant(v))==v
