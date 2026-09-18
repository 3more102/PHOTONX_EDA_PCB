def validate_keepout(k):
    x0,y0,x1,y1=k.bounds;issues=[]
    if x1<x0 or y1<y0:issues.append("KEEPOUT_INVALID_BOUNDS")
    if not k.id:issues.append("KEEPOUT_ID_EMPTY")
    return issues
