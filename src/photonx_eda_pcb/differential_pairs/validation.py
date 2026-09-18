def validate_pair(pair):
    issues=[]
    if pair.positive_net==pair.negative_net:issues.append("DIFF_PAIR_SAME_NET")
    if not 0<=pair.confidence<=1:issues.append("DIFF_PAIR_BAD_CONFIDENCE")
    return issues
