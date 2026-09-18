from photonx_eda_pcb.provenance_graph import build_provenance_graph
from photonx_eda_pcb.provenance_graph.merge import merge_graphs
def test_merge_dedups_edges():
    a=build_provenance_graph([{"object_id":"x","sources":["a"]}])
    b=build_provenance_graph([{"object_id":"x","sources":["a"]}])
    assert len(merge_graphs(a,b).edges)==1
