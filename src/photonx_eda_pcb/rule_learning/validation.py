def validate_learned_profile(p):
    issues=[]
    for r in p.rules.values():
        if r.value<=0:issues.append("LEARNED_RULE_NONPOSITIVE")
        if not 0<=r.confidence<=1:issues.append("LEARNED_RULE_CONFIDENCE_RANGE")
        if r.sample_count<=0:issues.append("LEARNED_RULE_NO_SAMPLES")
    return issues
