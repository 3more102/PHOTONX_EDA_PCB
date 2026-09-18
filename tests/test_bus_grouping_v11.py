from photonx_eda_pcb.bus_grouping import infer_buses,validate_bus
from photonx_eda_pcb.bus_grouping.coverage import index_coverage
def test_contiguous_bus():
    b=infer_buses({"n0":"DATA0","n1":"DATA1","n2":"DATA2"})[0]
    assert b.name=="DATA" and b.width==3 and b.confidence>=.8
    assert index_coverage(b)==1.0 and validate_bus(b)==[]
