def score_trend(health_items):
    scores=[x.score for x in health_items]
    return {"count":len(scores),"latest":scores[-1] if scores else None,"delta":round(scores[-1]-scores[-2],6) if len(scores)>=2 else None}
