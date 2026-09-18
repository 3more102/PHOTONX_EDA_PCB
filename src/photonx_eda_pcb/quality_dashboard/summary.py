def dashboard_summary(d):return {"overall_score":d.overall_score,"cards":{c.name:{"score":c.score,"status":c.status} for c in d.cards}}
