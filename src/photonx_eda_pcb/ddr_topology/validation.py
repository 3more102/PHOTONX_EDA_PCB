def validate_ddr_topology(t):
    issues=[]
    if not 0<=t.confidence<=1:issues.append("DDR_CONFIDENCE_RANGE")
    seen=set()
    for lane in t.lanes:
        for n in lane.nets:
            if n in seen:issues.append("DDR_NET_IN_MULTIPLE_LANES")
            seen.add(n)
        if not 0<=lane.confidence<=1:issues.append("DDR_LANE_CONFIDENCE_RANGE")
    return issues
