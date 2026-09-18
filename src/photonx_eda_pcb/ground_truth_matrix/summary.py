def summarize_results(results):
    items=list(results);ok=sum(r.passed for r in items)
    return {"total":len(items),"passed":ok,"failed":len(items)-ok,"pass_rate":1.0 if not items else round(ok/len(items),6)}
