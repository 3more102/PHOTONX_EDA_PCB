from photonx_eda_pcb.component_identity.model import ResolvedIdentity
from photonx_eda_pcb.protection_inference.model import ProtectionCandidate
from photonx_eda_pcb.fuse_analysis import analyze_fuses,validate_fuse
def test_polyfuse_resettable():
    p=ProtectionCandidate("F1","fuse",("VBUS","VIN"),.9,(),())
    ids={"F1":ResolvedIdentity("F1","ptc","polyfuse",None,None,.9)}
    f=analyze_fuses([p],ids)[0]
    assert f.resettable is True and validate_fuse(f)==[]
