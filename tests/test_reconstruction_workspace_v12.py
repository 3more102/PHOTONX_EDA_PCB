from photonx_eda_pcb.schematic_graph.model import SchematicGraph,ComponentNode,NetNode
from photonx_eda_pcb.schematic_pages.model import SchematicPageSet,SchematicPage
from photonx_eda_pcb.review_workflow.model import ReviewQueue,ReviewItem
from photonx_eda_pcb.reconstruction_workspace import build_workspace_view
def test_workspace_view():
    g=SchematicGraph({"U1":ComponentNode("U1")},{"N1":NetNode("N1")},[])
    pages=SchematicPageSet([SchematicPage("p","P",("U1",),("N1",))])
    q=ReviewQueue([ReviewItem("r","x","U1")])
    v=build_workspace_view(schematic_graph=g,blocks=[1],pages=pages,unresolved=["x"],review_queue=q)
    assert v.component_count==1 and v.page_count==1 and v.review_count==1
