from .model import EsdNetwork
def infer_esd_networks(protection_candidates,ground_nets=(),interface_nets=()):
    ground=set(map(str,ground_nets));interface=set(map(str,interface_nets));by={}
    for p in protection_candidates:
        if p.kind not in {"esd","tvs"}:continue
        nets=set(p.protected_nets);grounds=tuple(sorted(nets&ground))
        for n in sorted(nets&interface):by.setdefault(n,[]).append((p,grounds))
    out=[]
    for net,items in sorted(by.items()):
        comps=tuple(sorted(x[0].component_id for x in items));grounds=tuple(sorted({g for _,gs in items for g in gs}))
        score=.7+(.15 if grounds else 0)+min(.1,.03*len(comps))
        ev=["esd_or_tvs_identity","interface_net"]+(["ground_reference"] if grounds else [])
        out.append(EsdNetwork(net,comps,grounds,round(min(score,1),6),tuple(ev)))
    return out
