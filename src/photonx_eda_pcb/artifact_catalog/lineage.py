def dependency_edges(catalog):
    out=[]
    for name in catalog.names():
        a=catalog.get(name)
        for src in a.inputs:out.append((src,a.name))
    return sorted(out)
def missing_dependencies(catalog):return sorted({src for src,_ in dependency_edges(catalog) if src not in set(catalog.names())})
