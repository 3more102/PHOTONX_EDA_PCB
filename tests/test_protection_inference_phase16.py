from photonx_eda_pcb.component_identity.model import ResolvedIdentity
from photonx_eda_pcb.protection_inference import infer_protection,validate_protection
def test_tvs_interface_protection():
    ids={"D1":ResolvedIdentity("D1","tvs","TVS",None,None,.9)}
    p=infer_protection(ids,{"D1":["USB_DP","GND"]},["USB_DP"],[],["GND"])[0]
    assert p.kind=="tvs" and p.confidence>=.8
    assert validate_protection(p)==[]
