from .model import ClockCandidate
from .labels import label_clock_score
from .fanout import fanout_score
from .sources import source_score
def infer_clock_nets(net_data,min_confidence=.5):
    out=[]
    for item in net_data:
        score,ev=label_clock_score(item.get("label",""));e=list(ev)
        fs=fanout_score(item.get("fanout",0))
        if fs:score+=fs;e.append("fanout")
        ss=source_score(item.get("source_kind",""))
        if ss:score+=ss;e.append("clock_source")
        score=round(min(score,1.0),12)
        if score>=min_confidence:
            out.append(ClockCandidate(str(item["net_id"]),score,tuple(e),int(item.get("fanout",0)),item.get("frequency_hz")))
    return sorted(out,key=lambda x:(-x.confidence,x.net_id))
