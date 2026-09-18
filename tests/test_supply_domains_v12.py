from photonx_eda_pcb.supply_domains import partition_supply_domains,validate_supply_domain
from photonx_eda_pcb.supply_domains.coverage import domain_coverage
def test_supply_domains():
    pins={"U1":{"1":"+3V3","2":"GND"},"U2":{"1":"+5V","2":"GND"}}
    d=partition_supply_domains(["+3V3","+5V"],["GND"],pins)
    by={x.name:x for x in d}
    assert by["+3V3"].voltage==3.3 and by["+5V"].voltage==5.0
    assert domain_coverage(d,["U1","U2"])==1.0
    assert all(validate_supply_domain(x)==[] for x in d)
