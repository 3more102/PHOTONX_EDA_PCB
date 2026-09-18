from .model import ResolvedNetName
def resolve_net_name(net_id,candidates):
    items=[x for x in candidates if x.net_id==str(net_id) and x.name]
    if not items:return ResolvedNetName(str(net_id),None,0.0,(),())
    by={}
    for x in items:
        by.setdefault(x.name,[]).append(x)
    ranked=sorted(by.items(),key=lambda kv:(-max(x.confidence for x in kv[1]),kv[0]))
    name,group=ranked[0];confidence=max(x.confidence for x in group)
    conflicts=tuple(n for n,_ in ranked[1:])
    return ResolvedNetName(str(net_id),name,round(confidence,12),tuple(sorted({x.source for x in group})),conflicts)
def resolve_all(net_ids,candidates):return [resolve_net_name(n,candidates) for n in sorted(map(str,net_ids))]
