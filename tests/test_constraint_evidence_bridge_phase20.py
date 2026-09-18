from photonx_eda_pcb.constraint_synthesis import synthesize_constraints
from photonx_eda_pcb.constraint_evidence_bridge import constraint_records,constraint_review_items
from photonx_eda_pcb.constraint_evidence_bridge.validation import validate_records
def test_constraint_bridge():
    s=synthesize_constraints(["n"],{"n":("signal",)})
    records=constraint_records(s)
    assert len(records)==1 and records[0].kind=="constraint_candidate"
    assert validate_records(records)==[]
    assert constraint_review_items(s)
