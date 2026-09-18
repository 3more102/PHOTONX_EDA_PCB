def pad_net_conflicts(evidence):
    nets={}
    for e in evidence:nets.setdefault(e.pad_id,set()).add(e.net_name)
    return {p:sorted(v) for p,v in nets.items() if len(v)>1}
