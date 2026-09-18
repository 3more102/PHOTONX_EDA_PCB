def result_report(results):
    vals=list(results)
    return {"cases":len(vals),"passed":sum(r.passed for r in vals),"failed":sum(not r.passed for r in vals)}
