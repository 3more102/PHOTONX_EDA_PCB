def route_evidence(route):
    return {"source_count":len(route.provenance.sources),"tool":route.tool,"plating":route.plated,"points":len(route.points),"width_mm":route.width_mm}
