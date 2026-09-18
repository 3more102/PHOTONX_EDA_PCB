def conformance_summary(results):
    items=list(results);ok=sum(r.passed for r in items)
    return {"total":len(items),"passed":ok,"failed":len(items)-ok,"failures":[{"id":r.id,"differences":list(r.differences)} for r in items if not r.passed]}
