from photonx_eda_pcb.netlist_reconstruction.model import Netlist,NetConnection
from photonx_eda_pcb.schematic_graph import build_schematic_graph
from photonx_eda_pcb.signal_conditioning import infer_conditioning_stages,validate_stage
class C:
    def __init__(self,id,kind,value=""): self.id=id; self.kind=kind; self.value=value
def test_rc_and_ferrite_detection():
    n=Netlist({"n":[NetConnection("R1","1"),NetConnection("C1","1")],"p":[NetConnection("FB1","1")],"q":[NetConnection("FB1","2")]},{})
    g=build_schematic_graph(n)
    out=infer_conditioning_stages([C("R1","resistor"),C("C1","capacitor"),C("FB1","ferrite bead")],g,{"n":("analog",)})
    kinds={x.kind for x in out}
    assert {"rc_filter","ferrite_filter"}<=kinds
    assert all(validate_stage(x)==[] for x in out)
