def corpus_results_summary(results):
    items=list(results);ok=sum(r.passed for r in items)
    return {"total":len(items),"passed":ok,"failed":len(items)-ok,"pass_rate":1.0 if not items else round(ok/len(items),6)}
def failure_report(results):
    return [{"case_id":r.case_id,"differences":[list(x) for x in r.differences]} for r in results if not r.passed]
