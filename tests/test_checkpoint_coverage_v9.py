from photonx_eda_pcb.review_checkpoints.model import ReviewCheckpoint
from photonx_eda_pcb.review_checkpoints.coverage import checkpoint_coverage
def test_checkpoint_coverage():
    assert checkpoint_coverage(ReviewCheckpoint("x","x",("a","b")),["a"])==.5
