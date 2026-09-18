import networkx as nx
from photonx_eda_pcb.page_partitioning.model import PagePartition
from photonx_eda_pcb.schematic_autolayout import build_layout_plan,apply_layout,validate_autolayout
def test_autolayout_flow():
    g=nx.Graph();g.add_edges_from([("C:U1","N:N1"),("N:N1","C:R1"),("C:R1","N:N2"),("N:N2","C:U2")])
    p=PagePartition("p","P",(),("R1","U1","U2"),("N1","N2"),3)
    r=apply_layout(g,build_layout_plan(p))
    assert set(r.positions)=={"R1","U1","U2"} and len(r.routes)==2
    assert validate_autolayout(r)==[]
