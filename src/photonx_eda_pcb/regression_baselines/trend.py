def metric_trend(observations,key):
    vals=[x[key] for x in observations if key in x and isinstance(x[key],(int,float))]
    return {"count":len(vals),"min":min(vals) if vals else None,"max":max(vals) if vals else None,"latest":vals[-1] if vals else None}
