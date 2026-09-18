import networkx as nx
from photonx_eda_pcb.subgraph_fingerprints import fingerprint_around_component
from photonx_eda_pcb.subgraph_fingerprints.similarity import fingerprint_similarity
from photonx_eda_pcb.subgraph_fingerprints.differences import fingerprint_differences
class I:
    def __init__(self,kind):self.kind=kind
def test_semantic_difference_visible():
    g=nx.Graph();g.add_edges_from([("C:R1","N:A"),("N:A","C:D1"),("C:R2","N:B"),("N:B","C:C1")])
    for n in g.nodes:g.nodes[n]["kind"]="component" if n.startswith("C:") else "net"
    ids={"R1":I("resistor"),"D1":I("led"),"R2":I("resistor"),"C1":I("capacitor")}
    a=fingerprint_around_component(g,"R1",2,ids,{})
    b=fingerprint_around_component(g,"R2",2,ids,{})
    assert a.topology_hash==b.topology_hash and a.semantic_hash!=b.semantic_hash
    assert fingerprint_similarity(a,b)<1
    assert "semantics" in fingerprint_differences(a,b)
