from photonx_eda_pcb.models import BoardModel,PadCandidate,Point
from photonx_eda_pcb.production_board_validation import validate_production_board
def test_production_validation_requires_evidence_and_connectivity():
    r=validate_production_board(BoardModel(pads=[PadCandidate("P1",Point(0,0),1,1,"C","F.Cu")]))
    assert not r.passed
    assert "PRODUCTION_OUTLINE_REQUIRED" in r.blockers
    assert "PRODUCTION_CONNECTIVITY_REQUIRED" in r.blockers
    assert "PRODUCTION_PROVENANCE_COVERAGE" in r.blockers
