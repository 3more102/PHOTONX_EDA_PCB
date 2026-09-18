def risk_report(r):return {"score":r.score,"level":r.level,"items":[i.__dict__ for i in r.items]}
