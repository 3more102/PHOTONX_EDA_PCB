from photonx_eda_pcb.production_release_profiles import development_profile,research_profile,ReleaseEvidence
from photonx_eda_pcb.production_release_profiles.matrix import evaluate_all
def test_release_profile_matrix():
    e=ReleaseEvidence({},{"provenance_coverage":.6,"completeness":.6},0,True,True)
    d=evaluate_all([development_profile(),research_profile()],e)
    assert [x.profile for x in d]==["development","research"] and all(x.passed for x in d)
