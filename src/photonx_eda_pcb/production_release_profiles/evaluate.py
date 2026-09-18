from photonx_eda_pcb.quality_gate.decision import evaluate_gate
from .model import ReleaseDecision
def evaluate_release_profile(profile,evidence):
    gate=evaluate_gate(evidence.issue_counts,evidence.metrics,profile.thresholds,evidence.regression_failures)
    blockers=[x.code for x in gate.findings if x.severity=="error"]
    warnings=[x.code for x in gate.findings if x.severity!="error"]
    checks=[
        ("TESTS_NOT_PASSED",profile.require_tests,evidence.tests_passed),
        ("NONDETERMINISTIC_OUTPUT",profile.require_determinism,evidence.deterministic),
        ("UNSUPPORTED_CRITICAL_SYNTAX",profile.require_zero_unsupported,evidence.unsupported_critical==0),
        ("PROVENANCE_INCOMPLETE",profile.require_provenance_complete,evidence.provenance_complete),
        ("MANDATORY_REVIEWS_OPEN",profile.require_review_closed,evidence.mandatory_reviews_closed),
        ("ROUNDTRIP_FAILED",profile.require_roundtrip,evidence.roundtrip_passed),
        ("GROUND_TRUTH_FAILED",profile.require_ground_truth,evidence.ground_truth_passed),
    ]
    blockers.extend(code for code,required,ok in checks if required and not ok)
    return ReleaseDecision(profile.name,not blockers,tuple(blockers),tuple(warnings))
