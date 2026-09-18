from photonx_eda_pcb.netlist_reconstruction.model import Netlist,NetConnection
from photonx_eda_pcb.schematic_graph import build_schematic_graph
from photonx_eda_pcb.digital_bias_networks import infer_digital_bias,validate_bias
class C:
    id="R1"; kind="resistor"; value="10K"
def test_pull_up_detection():
    n=Netlist({"sig":[NetConnection("R1","1")],"vdd":[NetConnection("R1","2")]},{})
    g=build_schematic_graph(n)
    out=infer_digital_bias([C()],g,["vdd"],["gnd"],{"sig":("reset",)})
    assert out[0].kind=="pull_up" and out[0].value_ohm==10000
    assert validate_bias(out[0])==[]
