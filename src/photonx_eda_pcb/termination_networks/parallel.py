def parallel_termination_candidates(components,schematic_graph,reference_nets,signal_roles=None):
    from .model import TerminationCandidate
    from .values import parse_resistance
    from .topology import component_nets
    refs=set(map(str,reference_nets));signal_roles=signal_roles or {};out=[]
    for c in components:
        if "resistor" not in str(getattr(c,"kind","")).lower():continue
        nets=component_nets(schematic_graph,getattr(c,"id",""))
        if len(nets)!=2 or not refs.intersection(nets):continue
        other=next((n for n in nets if n not in refs),None)
        if other is None:continue
        roles=signal_roles.get(other,())
        if not any("high_speed" in r or "clock" in r or "protocol:" in r for r in roles):continue
        value=parse_resistance(getattr(c,"value",None))
        out.append(TerminationCandidate(str(c.id),"parallel",nets,value,.72,("reference_net","signal_role")))
    return out
