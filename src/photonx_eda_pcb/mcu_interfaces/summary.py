def interface_summary(items):
    by={}
    for x in items:by.setdefault(x.component_id,[]).append(x.protocol)
    return {k:sorted(set(v)) for k,v in sorted(by.items())}
