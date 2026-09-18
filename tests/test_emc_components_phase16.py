from photonx_eda_pcb.protection_inference.model import ProtectionCandidate
from photonx_eda_pcb.emc_components import infer_emc_components,validate_emc
def test_ferrite_emc_candidate():
    p=ProtectionCandidate("FB1","ferrite",("VDD_RAW","VDD"),.8,(),())
    e=infer_emc_components([p])[0]
    assert e.kind=="ferrite" and validate_emc(e)==[]
