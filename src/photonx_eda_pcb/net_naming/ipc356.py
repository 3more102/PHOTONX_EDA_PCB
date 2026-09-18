from .model import NetNameCandidate
from .normalize import normalize_net_name
def candidates_from_ipc356(records):
    out=[]
    for r in records:
        net=str(getattr(r,"net","") or getattr(r,"net_name","") or "")
        obj=str(getattr(r,"object_id","") or getattr(r,"id","") or "")
        if net and obj:out.append(NetNameCandidate(obj,normalize_net_name(net),.98,"ipc356","electrical_test_net"))
    return out
