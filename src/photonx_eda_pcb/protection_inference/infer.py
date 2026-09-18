from .model import ProtectionCandidate
from .kinds import protection_kind
def infer_protection(identity_by_id,component_nets,external_nets=(),power_nets=(),ground_nets=()):
    external=set(map(str,external_nets));power=set(map(str,power_nets));ground=set(map(str,ground_nets));out=[]
    for cid,identity in sorted(identity_by_id.items()):
        kind=protection_kind(identity)
        if kind is None:continue
        nets=tuple(sorted(set(map(str,component_nets.get(cid,())))))
        score=.6;ev=["component_identity"];ass=[]
        if set(nets)&external:score+=.15;ev.append("external_interface_net")
        if set(nets)&power:score+=.1;ev.append("power_net")
        if set(nets)&ground:score+=.1;ev.append("ground_net")
        if not nets:ass.append("connectivity_unknown")
        out.append(ProtectionCandidate(str(cid),kind,nets,round(min(score,1),6),tuple(ev),tuple(ass)))
    return out
