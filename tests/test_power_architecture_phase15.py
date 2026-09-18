from photonx_eda_pcb.supply_domains.model import SupplyDomain
from photonx_eda_pcb.regulator_inference.model import RegulatorCandidate
from photonx_eda_pcb.rail_dependencies import infer_rail_dependencies
from photonx_eda_pcb.power_architecture import build_power_architecture,validate_power_architecture
def test_power_architecture_build():
    domains=[SupplyDomain("VBUS",("VBUS",),("GND",),("U1",),5,.9),SupplyDomain("+3V3",("+3V3",),("GND",),("U2",),3.3,.9)]
    regs=[RegulatorCandidate("U1","ldo",("VBUS",),("+3V3",),(),(),.9,())]
    deps=infer_rail_dependencies(regs)
    a=build_power_architecture(domains,regs,deps)
    assert set(a.rails)=={"VBUS","+3V3"} and len(a.stages)==1 and a.confidence>0
    assert validate_power_architecture(a)==[]
