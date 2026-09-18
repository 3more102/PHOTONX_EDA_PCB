def group_decoupling(observations,qualities=(),bulk_threshold_f=1e-6):
    from .model import DecouplingGroup
    qmap={x.component_id:x for x in qualities};by={}
    for o in observations:by.setdefault(o.power_net,[]).append(o)
    out=[]
    for net,items in sorted(by.items()):
        comps=tuple(sorted(o.component_id for o in items));vals=[o.capacitance_f for o in items if o.capacitance_f is not None]
        total=sum(vals) if vals else None
        bulk=tuple(sorted(o.component_id for o in items if o.capacitance_f is not None and o.capacitance_f>=bulk_threshold_f))
        qs=[qmap[o.component_id].score*qmap[o.component_id].confidence for o in items if o.component_id in qmap]
        quality=round(sum(qs)/len(qs),6) if qs else 0.0
        confidence=round(min(1.0,.5+(.2 if vals else 0)+(.2 if qs else 0)),6)
        out.append(DecouplingGroup(net,comps,total,bulk,quality,confidence))
    return out
