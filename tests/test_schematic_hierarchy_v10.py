from photonx_eda_pcb.schematic_graph.model import SchematicGraph,ComponentNode,NetNode
from photonx_eda_pcb.schematic_hierarchy import infer_hierarchy,validate_hierarchy
def test_hierarchy_groups_components():
    g=SchematicGraph({"U1":ComponentNode("U1","mcu"),"J1":ComponentNode("J1","connector"),"R1":ComponentNode("R1","resistor")},{"n1":NetNode("n1","SIG")},[("U1","1","n1"),("J1","1","n1"),("R1","1","n1")])
    r=infer_hierarchy(g)
    assert {b.name for b in r.blocks}>={"compute","io","logic"}
    assert validate_hierarchy(r)==[]
