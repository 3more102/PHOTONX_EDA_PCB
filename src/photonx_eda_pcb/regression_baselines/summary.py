def baseline_summary(results):
    items=list(results);ok=sum(r.passed for r in items)
    return {"total":len(items),"passed":ok,"failed":len(items)-ok}
