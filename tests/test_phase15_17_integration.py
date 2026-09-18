from photonx_eda_pcb.component_identity.model import ResolvedIdentity
from photonx_eda_pcb.regulator_inference import infer_regulators
from photonx_eda_pcb.rail_dependencies import infer_rail_dependencies
from photonx_eda_pcb.protection_inference import infer_protection
from photonx_eda_pcb.connector_pin_functions import infer_connector_pin_functions,resolve_pin_functions
def test_power_and_external_interface_flow():
    ids={"U1":ResolvedIdentity("U1","ldo","LDO",None,None,.95),"D1":ResolvedIdentity("D1","tvs","TVS",None,None,.9)}
    regs=infer_regulators(ids,{"U1":{"1":"VBUS","2":"+3V3"}},{"U1":{"1":"VIN","2":"VOUT"}})
    assert infer_rail_dependencies(regs)[0].downstream=="+3V3"
    prot=infer_protection(ids,{"D1":["VBUS","GND"]},["VBUS"],["VBUS"],["GND"])
    assert prot[0].kind=="tvs"
    pins=resolve_pin_functions(infer_connector_pin_functions("J1",{"1":"VBUS","2":"GND"},net_labels={"VBUS":"VBUS","GND":"GND"},power_nets=["VBUS"],ground_nets=["GND"]))
    assert {x.function for x in pins}=={"power","ground"}
