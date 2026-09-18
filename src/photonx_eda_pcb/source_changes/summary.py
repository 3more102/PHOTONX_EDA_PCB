def change_summary(cs):
    out={"total":len(cs.changes),"added":0,"removed":0,"modified":0}
    for c in cs.changes:out[c.change_type]=out.get(c.change_type,0)+1
    return out
