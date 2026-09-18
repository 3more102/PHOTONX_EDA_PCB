def endpoint_coverage(link):
    comps={e.component_id for e in link.endpoints}
    return {"components":len(comps),"nets":len(link.nets),"endpoints":len(link.endpoints)}
