def si_risk_report(items):return [{"net_id":x.net_id,"score":x.score,"level":x.level,"confidence":x.confidence,"factors":dict(x.factors)} for x in sorted(items,key=lambda x:(-x.score,x.net_id))]
