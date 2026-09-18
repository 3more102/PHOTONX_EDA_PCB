from photonx_eda_pcb.connector_pin_functions import infer_connector_pin_functions,resolve_pin_functions
def test_pin_conflict_preserved():
    r=resolve_pin_functions(infer_connector_pin_functions("J1",{"1":"X"},net_labels={"X":"GND"},power_nets=["X"],ground_nets=["X"]))[0]
    assert r.function=="ground" and "power" in r.conflicts
