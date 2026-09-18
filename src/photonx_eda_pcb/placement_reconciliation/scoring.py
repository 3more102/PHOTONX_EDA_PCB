def placement_score(deltas):
    if not deltas:return 1.0
    ok=sum(x.code=="OK" for x in deltas)
    return round(ok/len(deltas),6)
