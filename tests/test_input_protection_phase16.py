from photonx_eda_pcb.connector_paths.model import ConnectorPath
from photonx_eda_pcb.protection_inference.model import ProtectionCandidate
from photonx_eda_pcb.input_protection import analyze_input_protection,validate_input_path
def test_connector_protection_chain():
    path=ConnectorPath("J1","U1",("C:J1","N:USB","C:D1","N:USB_IN","C:U1"),4,.8)
    p=ProtectionCandidate("D1","tvs",("USB","GND"),.9,(),())
    x=analyze_input_protection([path],[p])[0]
    assert x.protection_components==("D1",) and x.kinds==("tvs",)
    assert validate_input_path(x)==[]
