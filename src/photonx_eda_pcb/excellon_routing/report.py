from .measure import route_length_mm,route_segment_count
def route_report(routes):
    return [{"id":r.id,"points":[list(p) for p in r.points],"width_mm":r.width_mm,"plated":r.plated,"tool":r.tool,"segments":route_segment_count(r),"length_mm":route_length_mm(r)} for r in routes]
