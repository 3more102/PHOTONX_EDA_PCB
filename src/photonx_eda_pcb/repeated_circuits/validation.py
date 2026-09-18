def validate_group(g):
    issues=[]
    if len(g.instances)<2:issues.append("REPEATED_GROUP_TOO_SMALL")
    if len({x.id for x in g.instances})!=len(g.instances):issues.append("REPEATED_DUPLICATE_INSTANCE")
    if not 0<=g.similarity<=1 or not 0<=g.confidence<=1:issues.append("REPEATED_SCORE_RANGE")
    return issues
