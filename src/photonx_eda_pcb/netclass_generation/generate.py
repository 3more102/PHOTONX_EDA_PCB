def generate_netclasses(constraint_set,roles_by_net=None):
    from .model import GeneratedNetClass
    roles_by_net=roles_by_net or {};groups={}
    for c in constraint_set.constraints:
        roles=tuple(sorted(roles_by_net.get(c.net_id,())))
        key=(round(float(c.min_width_mm or .15),6),round(float(c.clearance_mm or .15),6),roles)
        groups.setdefault(key,[]).append(c)
    out=[]
    for i,(key,items) in enumerate(sorted(groups.items(),key=lambda x:x[0])):
        width,clearance,roles=key
        label=next((r for r in roles if r in {"power","ground","clock","reset","differential"}),"signal")
        name=f"{label}_{i+1}"
        conf=round(sum(x.confidence for x in items)/len(items),12)
        out.append(GeneratedNetClass(name,tuple(sorted(x.net_id for x in items)),width,clearance,conf,roles))
    return out
