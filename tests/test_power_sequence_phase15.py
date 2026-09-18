from photonx_eda_pcb.regulator_inference.model import RegulatorCandidate
from photonx_eda_pcb.power_sequences import infer_power_sequence,validate_sequence
from photonx_eda_pcb.power_sequences.order import topological_order
def test_enable_based_sequence():
    r=RegulatorCandidate("U2","ldo",("VIN",),("VCORE",),("CORE_EN",),(),.9,())
    s=infer_power_sequence([r],{"CORE_EN":"+3V3"})
    assert s[0].before=="+3V3" and s[0].after=="VCORE"
    assert topological_order(s)==("+3V3","VCORE") and validate_sequence(s)==[]
