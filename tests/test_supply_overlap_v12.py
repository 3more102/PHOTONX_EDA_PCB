from photonx_eda_pcb.supply_domains import partition_supply_domains
from photonx_eda_pcb.supply_domains.overlap import overlapping_components
def test_multi_supply_component_visible():
    d=partition_supply_domains(["VDD1","VDD2"],["GND"],{"U1":{"1":"VDD1","2":"VDD2"}})
    assert overlapping_components(d)["U1"]==("VDD1","VDD2")
