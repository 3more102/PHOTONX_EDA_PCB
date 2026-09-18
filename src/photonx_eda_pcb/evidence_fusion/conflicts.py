def conflicting_claims(items):
    by_source={}
    for i in items:by_source.setdefault(i.source,set()).add(i.claim)
    return {s:sorted(v) for s,v in by_source.items() if len(v)>1}
