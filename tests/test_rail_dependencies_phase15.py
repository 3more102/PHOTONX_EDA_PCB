from photonx_eda_pcb.regulator_inference.model import RegulatorCandidate
from photonx_eda_pcb.rail_dependencies import infer_rail_dependencies,validate_dependencies
from photonx_eda_pcb.rail_dependencies.roots import root_rails
def test_regulator_creates_rail_dependency():
    r=RegulatorCandidate("U1","ldo",("VBUS",),("+3V3",),(),(),.9,())
    d=infer_rail_dependencies([r])
    assert [(x.upstream,x.downstream) for x in d]==[("VBUS","+3V3")]
    assert root_rails(d)==("VBUS",) and validate_dependencies(d)==[]
