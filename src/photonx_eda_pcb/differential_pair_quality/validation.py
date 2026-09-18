def validate_pair_quality(x):
    issues=[]
    if x.positive_net==x.negative_net:issues.append("DIFF_QUALITY_SAME_NET")
    if not 0<=x.score<=1:issues.append("DIFF_QUALITY_SCORE_RANGE")
    if x.via_mismatch<0:issues.append("DIFF_QUALITY_NEGATIVE_VIA_MISMATCH")
    return issues
