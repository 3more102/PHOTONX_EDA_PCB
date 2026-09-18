from .model import ChannelCandidate
from .classify import classify_channel
def detect_channels(groups,identity_by_id=None,roles_by_net=None):
    identity_by_id=identity_by_id or {};roles_by_net=roles_by_net or {};out=[]
    for g in groups:
        kinds=[];roles=set();diffs=set()
        for inst in g.instances:
            diffs.update(inst.differences)
            for c in inst.components:kinds.append(str(getattr(identity_by_id.get(c),"kind","unknown") or "unknown"))
            for n in inst.nets:roles.update(roles_by_net.get(n,()))
        kind=classify_channel(kinds,roles)
        conf=g.confidence*(.9 if kind!="repeated_channel" else .75)
        out.append(ChannelCandidate("channel:"+g.id,tuple(i.id for i in g.instances),kind,round(conf,6),("repeated_circuit_group",)+(("semantic_classification",) if kind!="repeated_channel" else ()),tuple(sorted(diffs))))
    return sorted(out,key=lambda x:(-x.confidence,x.id))
