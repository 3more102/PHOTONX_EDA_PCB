from .model import ProjectHealth
def compute_health(metrics):
    items=list(metrics);den=sum(max(0.0,m.weight) for m in items)
    score=0.0 if den<=0 else sum(max(0,min(1,m.score))*max(0,m.weight) for m in items)/den
    return ProjectHealth(items,round(score,6))
