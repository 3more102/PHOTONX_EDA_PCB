from .model import ResolvedIdentity
from .scoring import weighted_confidence
def _pick(items,field):
    vals={}
    for c in items:
        v=getattr(c,field)
        if v in (None,""):continue
        if field=="kind" and str(v).lower()=="unknown":continue
        vals.setdefault(str(v),[]).append(c)
    if not vals:return None,0.0,()
    ranked=sorted(vals.items(),key=lambda kv:(-max(weighted_confidence(x) for x in kv[1]),kv[0]))
    value,group=ranked[0]
    return value,max(weighted_confidence(x) for x in group),tuple(x for x,_ in ranked[1:])
def resolve_identity(component_id,candidates):
    items=[c for c in candidates if c.component_id==str(component_id)]
    kind,kc,kconf=_pick(items,"kind");value,vc,vconf=_pick(items,"value");fp,fc,fconf=_pick(items,"footprint");mpn,mc,mconf=_pick(items,"mpn")
    fields=[x for x in (kc,vc,fc,mc) if x>0];confidence=round(sum(fields)/len(fields),12) if fields else 0.0
    conflicts=tuple(sorted(set(kconf+vconf+fconf+mconf)))
    return ResolvedIdentity(str(component_id),kind,value,fp,mpn,confidence,tuple(sorted({c.source for c in items})),conflicts)
def resolve_identities(component_ids,candidates):return [resolve_identity(cid,candidates) for cid in sorted(map(str,component_ids))]
