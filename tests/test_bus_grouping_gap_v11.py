from photonx_eda_pcb.bus_grouping import infer_buses
from photonx_eda_pcb.bus_grouping.coverage import index_coverage
def test_bus_gap_visible():
    b=infer_buses({"n0":"A0","n2":"A2"})[0]
    assert b.confidence<.8 and index_coverage(b)<1
