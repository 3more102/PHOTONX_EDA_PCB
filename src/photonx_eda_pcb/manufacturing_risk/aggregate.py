from .model import ManufacturingRisk
def aggregate_risk(items):
    x=list(items);score=0.0 if not x else sum(max(0,min(1,i.score)) for i in x)/len(x)
    level="high" if score>=.7 else "medium" if score>=.35 else "low" if score>0 else "none"
    return ManufacturingRisk(x,round(score,6),level)
