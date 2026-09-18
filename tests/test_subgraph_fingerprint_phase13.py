import networkx as nx
from photonx_eda_pcb.subgraph_fingerprints import fingerprint_around_component,validate_fingerprint
class I:
    def __init__(self,kind):self.kind=kind
def _graph():
    g=nx.Graph()
    g.add_edges_from([("C:R1","N:A"),("N:A","C:D1"),("C:R2","N:B"),("N:B","C:D2")])
    for n in g.nodes:g.nodes[n]["kind"]="component" if n.startswith("C:") else "net"
    return g
def test_repeated_branch_fingerprints_match():
    g=_graph();ids={"R1":I("resistor"),"D1":I("led"),"R2":I("resistor"),"D2":I("led")}
    a=fingerprint_around_component(g,"R1",2,ids,{})
    b=fingerprint_around_component(g,"R2",2,ids,{})
    assert a.topology_hash==b.topology_hash and a.semantic_hash==b.semantic_hash
    assert validate_fingerprint(a)==[]
