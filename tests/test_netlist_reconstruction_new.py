from photonx_eda_pcb.netlist_reconstruction.builder import build_netlist
from photonx_eda_pcb.netlist_reconstruction.topology import dangling_nets
from photonx_eda_pcb.netlist_reconstruction.validation import validate_netlist

def test_netlist_builder():
    n=build_netlist({'U1':{'1':'N1','2':'N2'},'R1':{'1':'N1','2':'N3'}})
    assert len(n.nets['N1'])==2
    assert dangling_nets(n)==['N2','N3']
    assert validate_netlist(n)==[]
