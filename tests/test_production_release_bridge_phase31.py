from photonx_eda_pcb.production_board_validation.model import ProductionValidationResult
from photonx_eda_pcb.production_board_validation.release import release_decision_from_validation
def test_production_result_can_feed_release_profile():
    r=ProductionValidationResult(True,[],[],{"provenance_coverage":1.0})
    d=release_decision_from_validation(r,tests_passed=True,deterministic=True,unsupported_critical=0,review_closed=True,roundtrip_passed=True,ground_truth_passed=True)
    assert d.passed
