def eco_summary(e):
    return {"name":e.name,"changes":len(e.changes),"approved":sum(x.approved for x in e.changes),"pending":sum(not x.approved for x in e.changes)}
