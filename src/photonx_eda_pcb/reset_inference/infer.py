from .labels import reset_label
from .fanout import reset_fanout_boost
from .model import ResetCandidate
def infer_reset_nets(net_data,min_confidence=.5):
    out=[]
    for x in net_data:
        active,score,ev=reset_label(x.get("label",""));e=list(ev)
        boost=reset_fanout_boost(x.get("fanout",0))
        if boost:score+=boost;e.append("fanout")
        if x.get("source_kind") in {"supervisor","reset_controller"}:score+=.2;e.append("reset_source")
        score=round(min(score,1),12)
        if score>=min_confidence:out.append(ResetCandidate(str(x["net_id"]),active,score,int(x.get("fanout",0)),tuple(e)))
    return sorted(out,key=lambda x:(-x.confidence,x.net_id))
