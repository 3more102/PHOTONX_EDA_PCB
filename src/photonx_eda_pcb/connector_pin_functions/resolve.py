from .model import ResolvedPinFunction
def resolve_pin_functions(candidates):
    by={}
    for c in candidates:by.setdefault((c.connector_id,c.pin,c.net_id),[]).append(c)
    out=[]
    for key,items in sorted(by.items()):
        ranked=sorted(items,key=lambda x:(-x.confidence,x.function))
        best=ranked[0]
        conflicts=tuple(sorted({x.function for x in ranked[1:] if x.function!=best.function and x.confidence>0}))
        ev=tuple(sorted({e for x in ranked if x.function==best.function for e in x.evidence}))
        out.append(ResolvedPinFunction(*key,best.function if best.confidence>0 else None,best.confidence,ev,conflicts))
    return out
