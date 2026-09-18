from .model import SignalRole
def synthesize_roles(net_ids,*,clock=(),reset=(),buses=(),protocols=(),power=(),ground=()):
    map={str(n):set() for n in net_ids};ev={str(n):[] for n in net_ids}
    for c in clock:map.setdefault(c.net_id,set()).add("clock");ev.setdefault(c.net_id,[]).append("clock_inference")
    for r in reset:map.setdefault(r.net_id,set()).add("reset");ev.setdefault(r.net_id,[]).append("reset_inference")
    for b in buses:
        for n in b.net_ids:map.setdefault(n,set()).add("bus:"+b.name);ev.setdefault(n,[]).append("bus_grouping")
    for p in protocols:
        for n in p.net_ids:map.setdefault(n,set()).add("protocol:"+p.protocol);ev.setdefault(n,[]).append("protocol_detection")
    for n in power:map.setdefault(str(n),set()).add("power");ev.setdefault(str(n),[]).append("power_intent")
    for n in ground:map.setdefault(str(n),set()).add("ground");ev.setdefault(str(n),[]).append("ground_intent")
    out=[]
    for n in sorted(map):
        roles=tuple(sorted(map[n]));confidence=min(1.0,.4+.12*len(roles)) if roles else 0.0
        out.append(SignalRole(n,roles,round(confidence,6),tuple(sorted(set(ev.get(n,()))))))
    return out
