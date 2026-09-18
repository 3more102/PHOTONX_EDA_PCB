from photonx_eda_pcb.bom.model import BomItem
from photonx_eda_pcb.component_identity.from_bom import candidates_from_bom
def test_bom_candidates():
    c=candidates_from_bom([BomItem(("R1","R2"),"10k","R_0603","ABC","M",2)])
    assert len(c)==2 and all(x.source=="bom" for x in c)
