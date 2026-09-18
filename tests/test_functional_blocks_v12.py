import networkx as nx
from photonx_eda_pcb.functional_blocks import cluster_functional_blocks,validate_block
class I:
    def __init__(self,kind):self.kind=kind
def test_functional_block_clustering():
    g=nx.Graph();g.add_edges_from([("C:U1","N:N1"),("N:N1","C:J1"),("C:U2","N:N2")])
    ids={"U1":I("mcu"),"J1":I("connector"),"U2":I("sensor")}
    b=cluster_functional_blocks(g,ids,{})
    assert len(b)==2 and any(x.kind=="interface" for x in b)
    assert all(validate_block(x)==[] for x in b)
