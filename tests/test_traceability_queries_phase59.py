from photonx_eda_pcb.traceability_matrix import build_traceability_matrix
from photonx_eda_pcb.traceability_matrix.queries import links_for_object,unresolved_traceability
def test_traceability_queries():
    m=build_traceability_matrix([{"claim_id":"c","source_ids":["s"],"object_ids":["U1"],"confidence":.7}])
    assert links_for_object(m,"U1")[0].claim_id=="c"
    assert unresolved_traceability(m)[0].claim_id=="c"
