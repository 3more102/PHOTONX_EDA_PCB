from .model import TerminationCandidate
from .values import parse_resistance
from .topology import component_nets
def infer_terminations(components,schematic_graph,signal_roles=None,diff_pairs=()):
    signal_roles=signal_roles or {};pair_nets={n for p in diff_pairs for n in (p.positive_net,p.negative_net)}
    out=[]
    for c in components:
        kind=str(getattr(c,"kind","") or "").lower()
        if "resistor" not in kind and kind not in {"r","res"}:continue
        nets=component_nets(schematic_graph,getattr(c,"id",""))
        if len(nets)!=2:continue
        value=parse_resistance(getattr(c,"value",None))
        roles=set(r for n in nets for r in signal_roles.get(n,()))
        tkind=None;score=.35;ev=["two_net_resistor"]
        if pair_nets and set(nets)<=pair_nets:
            tkind="differential_or_series";score+=.3;ev.append("differential_pair_context")
        elif any("clock" in r or "high_speed" in r or "protocol:" in r for r in roles):
            tkind="series";score+=.25;ev.append("high_speed_context")
        if value is not None and 10<=value<=200:
            score+=.2;ev.append("termination_value_range")
        if tkind:
            out.append(TerminationCandidate(str(c.id),tkind,nets,value,round(min(score,1),12),tuple(ev)))
    return sorted(out,key=lambda x:(-x.confidence,x.component_id))
