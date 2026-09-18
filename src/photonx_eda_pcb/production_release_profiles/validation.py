def validate_release_profile(p):
    issues=[]
    if not p.name.strip():issues.append("RELEASE_PROFILE_NAME_EMPTY")
    if not 0<=p.thresholds.min_provenance_coverage<=1:issues.append("RELEASE_PROFILE_PROVENANCE_RANGE")
    if not 0<=p.thresholds.min_completeness<=1:issues.append("RELEASE_PROFILE_COMPLETENESS_RANGE")
    return issues
