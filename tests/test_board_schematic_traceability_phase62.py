from photonx_eda_pcb.schematic_graph.model import SchematicGraph,ComponentNode,NetNode
from photonx_eda_pcb.schematic_pages.model import SchematicPage,SchematicPageSet
from photonx_eda_pcb.board_schematic_traceability import build_board_schematic_traceability
from photonx_eda_pcb.board_schematic_traceability.coverage import traceability_coverage
def test_board_schematic_traceability():
    g=SchematicGraph({"U1":ComponentNode("U1")},{"N1":NetNode("N1")},[("U1","1","N1")])
    ps=SchematicPageSet([SchematicPage("p","Main",("U1",),("N1",))])
    t=build_board_schematic_traceability(g,ps)
    assert traceability_coverage(t)==1.0
    assert len(t.traces)==2
