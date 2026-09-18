from photonx_eda_pcb.traceability_matrix import build_traceability_matrix,validate_traceability
from photonx_eda_pcb.traceability_matrix.coverage import traceability_coverage
def test_traceability_coverage():
    m=build_traceability_matrix([{"claim_id":"c1","source_ids":["s1"],"artifact_ids":["a1"],"review_ids":["r1"],"object_ids":["U1"],"confidence":.9},{"claim_id":"c2","source_ids":["s2"],"artifact_ids":[],"object_ids":["N1"],"confidence":.8}])
    c=traceability_coverage(m)
    assert c["source_coverage"]==1.0 and c["artifact_coverage"]==.5
    assert validate_traceability(m)==[]
