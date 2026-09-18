from photonx_eda_pcb.design_intent import infer_power_nets,infer_ground_nets,decoupling_candidates
def test_intent_helpers():
    labels={"n1":"+3V3","n2":"GND","n3":"SIG"}
    assert infer_power_nets(labels)==["n1"]
    assert infer_ground_nets(labels)==["n2"]
    kinds={"C1":"capacitor"}
    pins={"C1":{"1":"n1","2":"n2"}}
    assert decoupling_candidates(kinds,pins,["n1"],["n2"])==["C1"]
