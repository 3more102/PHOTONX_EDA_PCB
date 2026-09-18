from photonx_eda_pcb.production_release_profiles import manufacturing_candidate_profile,ReleaseEvidence,evaluate_release_profile
from photonx_eda_pcb.production_release_profiles.validation import validate_release_profile
def test_manufacturing_candidate_passes_complete_evidence():
    p=manufacturing_candidate_profile()
    e=ReleaseEvidence({},{"provenance_coverage":1.0,"completeness":1.0},0,True,True,0,True,True,True,True)
    d=evaluate_release_profile(p,e)
    assert d.passed and not d.blockers and validate_release_profile(p)==[]
