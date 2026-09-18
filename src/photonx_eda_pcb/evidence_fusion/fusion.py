from .model import FusedEvidence
def fuse_evidence(items):
    items=list(items)
    if not items:return FusedEvidence("",0.0,[],[])
    claim=items[0].claim
    rel=[i for i in items if i.claim==claim]
    group_best={}
    for i in rel:
        g=i.independent_group or i.source
        group_best[g]=max(group_best.get(g,0.0),max(0.0,min(1.0,float(i.confidence))))
    miss=1.0
    for c in group_best.values():miss*=1.0-c
    return FusedEvidence(claim,round(1.0-miss,12),sorted({i.source for i in rel}),sorted(group_best))
