def stress_report(results):
    vals=list(results)
    return {"cases":len(vals),"max_seconds":max((r["max_s"] for r in vals),default=0.0),"mean_seconds":sum((r["mean_s"] for r in vals),0.0)/len(vals) if vals else 0.0}
