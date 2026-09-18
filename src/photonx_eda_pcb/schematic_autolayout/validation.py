def validate_autolayout(result):
    issues=[];seen=set()
    for cid,pos in result.positions.items():
        if pos in seen:issues.append("AUTOLAYOUT_POSITION_COLLISION")
        seen.add(pos)
    if result.crossings<0:issues.append("AUTOLAYOUT_NEGATIVE_CROSSINGS")
    return issues
