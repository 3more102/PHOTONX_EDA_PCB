from .model import ReleaseProfile
from photonx_eda_pcb.quality_gate.thresholds import QualityThresholds
def development_profile():
    return ReleaseProfile("development",QualityThresholds(max_errors=10,max_warnings=500,min_provenance_coverage=0.0,min_completeness=0.0,max_regression_failures=10))
def research_profile():
    return ReleaseProfile("research",QualityThresholds(max_errors=0,max_warnings=250,min_provenance_coverage=.5,min_completeness=.5,max_regression_failures=0),require_tests=True,require_determinism=True)
def review_profile():
    return ReleaseProfile("review",QualityThresholds(max_errors=0,max_warnings=100,min_provenance_coverage=.75,min_completeness=.7,max_regression_failures=0),True,True,True,False,True,True,False)
def manufacturing_candidate_profile():
    return ReleaseProfile("manufacturing-export-candidate",QualityThresholds(max_errors=0,max_warnings=25,min_provenance_coverage=.95,min_completeness=.9,max_regression_failures=0),True,True,True,True,True,True,True)
