from photonx_eda_pcb.netlist_reconstruction.model import Netlist,NetConnection
from photonx_eda_pcb.schematic_graph import build_schematic_graph
from photonx_eda_pcb.termination_networks import infer_terminations,validate_termination
class C:
    def __init__(self,id,kind,value): self.id=id; self.kind=kind; self.value=value
def test_series_termination():
    n=Netlist({"a":[NetConnection("R1","1"),NetConnection("U1","1")],"b":[NetConnection("R1","2"),NetConnection("J1","1")]},{})
    g=build_schematic_graph(n)
    t=infer_terminations([C("R1","resistor","33R")],g,{"a":("clock",),"b":("clock",)})
    assert len(t)==1 and t[0].kind=="series" and t[0].value_ohm==33
    assert validate_termination(t[0])==[]
