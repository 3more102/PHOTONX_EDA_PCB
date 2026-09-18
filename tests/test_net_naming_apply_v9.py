from photonx_eda_pcb.netlist_reconstruction.model import Netlist
from photonx_eda_pcb.net_naming.model import ResolvedNetName
from photonx_eda_pcb.net_naming.apply import apply_resolved_names
def test_apply_resolved_name():
    n=Netlist({"n1":[]},{})
    q=apply_resolved_names(n,[ResolvedNetName("n1","GND",.9,("ipc356",),())])
    assert q.labels["n1"]=="GND"
