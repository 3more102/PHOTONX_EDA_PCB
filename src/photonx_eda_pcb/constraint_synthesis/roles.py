def primary_role(roles):
    r=set(roles)
    for x in ("ground","power","differential","clock","high_speed","reset"):
        if x in r:return x
    if any(y.startswith("protocol:") for y in r):return "high_speed"
    return "signal"
