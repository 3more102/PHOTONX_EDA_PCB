from photonx_eda_pcb.power_distribution.decoupling import decoupling_by_power_net
def test_decoupling_mapping():
    pins={"C1":{"1":"VDD","2":"GND"},"R1":{"1":"VDD","2":"SIG"}}
    kinds={"C1":"capacitor","R1":"resistor"}
    assert decoupling_by_power_net(pins,kinds,["VDD"],["GND"])=={"VDD":["C1"]}
