from .model import ReleaseCandidateDecision
def evaluate_release_candidate(candidate,*,audit_report=None,release_profile_decision=None,package_assessment=None):
    blockers=[];warnings=[]
    if not candidate.commit:blockers.append("RC_COMMIT_MISSING")
    if not candidate.artifacts:blockers.append("RC_ARTIFACTS_EMPTY")
    if audit_report is not None:
        from photonx_eda_pcb.release_audit.decision import failed_checks
        blockers.extend("AUDIT_"+x.upper() for x in failed_checks(audit_report))
    if release_profile_decision is not None:
        blockers.extend(release_profile_decision.blockers);warnings.extend(release_profile_decision.warnings)
    if package_assessment is not None:
        blockers.extend(package_assessment.blockers);warnings.extend(package_assessment.warnings)
    return ReleaseCandidateDecision(candidate.name,not blockers,tuple(sorted(set(blockers))),tuple(sorted(set(warnings))))
