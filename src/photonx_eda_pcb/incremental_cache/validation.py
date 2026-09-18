def validate_policy(policy):
    issues=[]
    if policy.max_entries<0:issues.append("CACHE_NEGATIVE_MAX_ENTRIES")
    if not str(policy.version):issues.append("CACHE_EMPTY_VERSION")
    return issues
