from photonx_eda_pcb.multilayer import LayerConnectivityGraph,connected_components
from photonx_eda_pcb.multilayer.via_edges import add_via_span_edges
def test_via_span_connectivity():
    graph=LayerConnectivityGraph(); add_via_span_edges(graph,"V1",["F.Cu","In1.Cu","B.Cu"])
    assert connected_components(graph)==(("V1@B.Cu","V1@F.Cu","V1@In1.Cu"),)
