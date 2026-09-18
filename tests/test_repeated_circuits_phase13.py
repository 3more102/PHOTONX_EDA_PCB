import networkx as nx
from photonx_eda_pcb.subgraph_fingerprints import fingerprint_around_component
from photonx_eda_pcb.repeated_circuits import detect_repeated_circuits,validate_group
class I:
    def __init__(self,kind):self.kind=kind
def test_detect_two_repeated_channels():
    g=nx.Graph();g.add_edges_from([("C:R1","N:A"),("N:A","C:D1"),("C:R2","N:B"),("N:B","C:D2")])
    for n in g.nodes:g.nodes[n]["kind"]="component" if n.startswith("C:") else "net"
    ids={"R1":I("resistor"),"D1":I("led"),"R2":I("resistor"),"D2":I("led")}
    fps=[fingerprint_around_component(g,x,2,ids,{}) for x in ("R1","R2")]
    groups=detect_repeated_circuits(fps)
    assert len(groups)==1 and len(groups[0].instances)==2
    assert validate_group(groups[0])==[]
