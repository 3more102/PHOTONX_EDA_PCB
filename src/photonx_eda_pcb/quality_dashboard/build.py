from .model import QualityCard,QualityDashboard
from .status import score_status
def build_dashboard(metrics):
    cards=[]
    for name,data in sorted(metrics.items()):
        score=float(data["score"] if isinstance(data,dict) else data)
        details=dict(data) if isinstance(data,dict) else {}
        details.pop("score",None)
        cards.append(QualityCard(str(name),round(min(1,max(0,score)),6),score_status(score),details))
    overall=0.0 if not cards else round(sum(c.score for c in cards)/len(cards),6)
    return QualityDashboard(cards,overall)
