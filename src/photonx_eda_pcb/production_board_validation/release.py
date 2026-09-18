from photonx_eda_pcb.production_release_profiles import manufacturing_candidate_profile,evaluate_release_profile
from photonx_eda_pcb.production_release_profiles.model import ReleaseEvidence
def release_decision_from_validation(result,*,tests_passed,deterministic,unsupported_critical,review_closed,roundtrip_passed,ground_truth_passed):
    e=ReleaseEvidence({"error":0 if result.passed else len(result.blockers)},{"provenance_coverage":result.metrics.get("provenance_coverage",0.0),"completeness":1.0 if result.passed else .5},0,bool(tests_passed),bool(deterministic),int(unsupported_critical),result.metrics.get("provenance_coverage",0)>=.95,bool(review_closed),bool(roundtrip_passed),bool(ground_truth_passed))
    return evaluate_release_profile(manufacturing_candidate_profile(),e)
