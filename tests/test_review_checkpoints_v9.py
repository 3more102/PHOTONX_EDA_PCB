from photonx_eda_pcb.review_checkpoints import ReviewCheckpoint,CheckpointStore,validate_checkpoint
from photonx_eda_pcb.review_checkpoints.decisions import add_decision,close_if_approved
def test_checkpoint_approval():
    c=ReviewCheckpoint("cp1","Connectivity",("nets","vias"))
    add_decision(c,"reviewer","approved","checked")
    assert close_if_approved(c) and c.closed
    s=CheckpointStore();s.add(c);assert s.get("cp1") is c
    assert validate_checkpoint(c)==[]
