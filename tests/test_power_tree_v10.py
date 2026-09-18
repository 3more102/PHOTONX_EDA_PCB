from photonx_eda_pcb.schematic_graph.model import SchematicGraph,ComponentNode,NetNode
from photonx_eda_pcb.power_tree import build_power_tree,validate_power_tree
from photonx_eda_pcb.power_tree.metrics import power_tree_metrics
def test_power_tree():
    g=SchematicGraph({"U1":ComponentNode("U1","ldo"),"R1":ComponentNode("R1","resistor")},{"p":NetNode("p","+3V3")},[("U1","out","p"),("R1","1","p")])
    t=build_power_tree(g,["p"])
    assert t.nodes["N:p"].voltage==3.3
    assert power_tree_metrics(t)["sources"]==1
    assert validate_power_tree(t)==[]
