from photonx_eda_pcb.manufacturing_review import run_manufacturing_review
from photonx_eda_pcb.manufacturing_review.markdown import to_markdown
def test_review_markdown():
    assert "Manufacturing Review" in to_markdown(run_manufacturing_review(drc_issues=["clearance"]))
