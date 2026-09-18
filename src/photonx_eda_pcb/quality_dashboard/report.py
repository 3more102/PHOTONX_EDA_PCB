def dashboard_report(d):return {"overall_score":d.overall_score,"cards":[{"name":c.name,"score":c.score,"status":c.status,"details":dict(c.details)} for c in d.cards]}
