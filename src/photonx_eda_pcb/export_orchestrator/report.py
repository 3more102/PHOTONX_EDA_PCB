def export_summary(results):
    ok=sum(r.success for r in results)
    return {"total":len(results),"passed":ok,"failed":len(results)-ok}
