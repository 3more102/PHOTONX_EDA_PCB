from photonx_eda_pcb.netlist_reconstruction.model import Netlist,NetConnection
from photonx_eda_pcb.schematic_graph import build_schematic_graph
from photonx_eda_pcb.termination_networks.parallel import parallel_termination_candidates
class C:
    def __init__(self,id): self.id=id; self.kind="resistor"; self.value="50"
def test_parallel_termination_to_ground():
    n=Netlist({"sig":[NetConnection("R1","1")],"gnd":[NetConnection("R1","2")]},{})
    g=build_schematic_graph(n)
    out=parallel_termination_candidates([C("R1")],g,["gnd"],{"sig":("high_speed",)})
    assert len(out)==1 and out[0].kind=="parallel"
