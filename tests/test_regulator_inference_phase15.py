from photonx_eda_pcb.component_identity.model import ResolvedIdentity
from photonx_eda_pcb.regulator_inference import infer_regulators,validate_regulator
def test_ldo_regulator_inference():
    ids={"U1":ResolvedIdentity("U1","ldo","LDO",None,None,.95)}
    pmap={"U1":{"1":"VIN","2":"VOUT","3":"EN","4":"FB","5":"GND"}}
    names={"U1":{"1":"VIN","2":"VOUT","3":"EN","4":"FB","5":"GND"}}
    r=infer_regulators(ids,pmap,names)[0]
    assert r.kind=="ldo" and r.input_nets==("VIN",) and r.output_nets==("VOUT",)
    assert r.enable_nets==("EN",) and r.feedback_nets==("FB",)
    assert validate_regulator(r)==[]
