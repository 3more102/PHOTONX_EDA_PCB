def component_roles(link):
    out={}
    for e in link.endpoints:out.setdefault(e.component_id,set()).add(e.role)
    return {k:tuple(sorted(v)) for k,v in sorted(out.items())}
