def interface_coverage(m):
    total=sum(len(x.get("pins",[])) for x in m.connectors.values())
    return 1.0 if total==0 else round((total-len(m.unresolved))/total,6)
