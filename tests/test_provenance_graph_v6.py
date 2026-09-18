from photonx_eda_pcb.provenance_graph import build_provenance_graph,impacted_objects,validate_graph
def test_provenance_impact():
    g=build_provenance_graph([{"object_id":"pad:1","sources":["top.gbr"],"evidence":[{"id":"e1","kind":"geometry","confidence":.8}]}])
    assert impacted_objects(g,"top.gbr")==["pad:1"]
    assert validate_graph(g)==[]
