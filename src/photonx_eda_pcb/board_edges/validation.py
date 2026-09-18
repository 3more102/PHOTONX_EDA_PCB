def validate_loops(loops):
    issues=[]
    for l in loops:
        if len(l.points)<3:issues.append("EDGE_LOOP_TOO_SMALL")
        if len(set(l.points))!=len(l.points):issues.append("EDGE_LOOP_DUPLICATE_VERTEX")
    return issues
