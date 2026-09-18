from .model import ConstraintCandidate,ConstraintSet
from .defaults import defaults_for
from .roles import primary_role
def synthesize_constraints(net_ids,roles_by_net=None,lengths=None,diff_pairs=(),observed_widths=None):
    roles_by_net=roles_by_net or {};lengths=lengths or {};observed_widths=observed_widths or {}
    pair_map={}
    for p in diff_pairs:
        pair_map[p.positive_net]=p
        pair_map[p.negative_net]=p
    out=[]
    for net in sorted(map(str,net_ids)):
        roles=roles_by_net.get(net,());role=primary_role(roles)
        d=defaults_for(role);ev=["role:"+role];confidence=.45
        widths=[float(x) for x in observed_widths.get(net,())]
        width=d.get("min_width_mm")
        if widths:
            width=max(width,min(widths));confidence+=.15;ev.append("observed_width")
        target=lengths.get(net)
        tol=None
        gap=d.get("diff_pair_gap_mm")
        if net in pair_map and target is not None:
            tol=max(.1,float(target)*.02);confidence+=.2;ev.append("diff_pair_length")
        if role in {"clock","high_speed","differential"}:confidence+=.1
        out.append(ConstraintCandidate(net,width,d.get("clearance_mm"),target,tol,gap,round(min(confidence,1),12),tuple(ev)))
    return ConstraintSet(out)
