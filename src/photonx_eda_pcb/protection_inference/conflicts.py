def protection_conflicts(items):
    by={}
    for x in items:by.setdefault(x.component_id,set()).add(x.kind)
    return {k:tuple(sorted(v)) for k,v in by.items() if len(v)>1}
