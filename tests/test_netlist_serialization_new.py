from photonx_eda_pcb.netlist_reconstruction.builder import build_netlist
from photonx_eda_pcb.netlist_reconstruction.serialization import netlist_json

def test_netlist_json_deterministic():
    n=build_netlist({'R1':{'2':'N2','1':'N1'}})
    a=netlist_json(n); b=netlist_json(n)
    assert a==b and 'N1' in a and 'N2' in a
