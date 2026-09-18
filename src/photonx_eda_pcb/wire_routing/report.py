from .segments import route_length
def route_report(items):return [{"net_id":r.net_id,"points":[list(p) for p in r.points],"style":r.style,"length":route_length(r)} for r in items]
