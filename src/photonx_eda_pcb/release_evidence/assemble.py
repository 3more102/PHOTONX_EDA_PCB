from photonx_eda_pcb.production_release_profiles.model import ReleaseEvidence
def assemble_release_evidence(*,issues,metrics,regression_failures=0,tests_passed=False,deterministic=False,unsupported_critical=0,provenance_complete=False,mandatory_reviews_closed=False,roundtrip_passed=False,ground_truth_passed=False):
    counts={}
    for x in issues:
        sev=getattr(x,"severity",x.get("severity","warning") if isinstance(x,dict) else "warning")
        counts[sev]=counts.get(sev,0)+1
    return ReleaseEvidence(counts,dict(metrics),int(regression_failures),bool(tests_passed),bool(deterministic),int(unsupported_critical),bool(provenance_complete),bool(mandatory_reviews_closed),bool(roundtrip_passed),bool(ground_truth_passed))
