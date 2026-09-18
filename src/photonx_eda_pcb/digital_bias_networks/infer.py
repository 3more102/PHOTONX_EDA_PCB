from photonx_eda_pcb.termination_networks.values import parse_resistance
def infer_digital_bias(components,schematic_graph,power_nets,ground_nets,signal_roles=None):
    from .model import BiasCandidate
    refs_power=set(map(str,power_nets));refs_ground=set(map(str,ground_nets));signal_roles=signal_roles or {};out=[]
    for c in components:
        if "resistor" not in str(getattr(c,"kind","")).lower():continue
        nets=tuple(sorted({nid for cid,_,nid in schematic_graph.pin_edges if cid==str(c.id)}))
        if len(nets)!=2:continue
        refs=refs_power|refs_ground
        linked=[n for n in nets if n in refs]
        if len(linked)!=1:continue
        ref=linked[0];sig=next(n for n in nets if n!=ref)
        if not signal_roles.get(sig):continue
        kind="pull_up" if ref in refs_power else "pull_down"
        out.append(BiasCandidate(str(c.id),sig,ref,kind,parse_resistance(getattr(c,"value",None)),.75))
    return sorted(out,key=lambda x:(x.net_id,x.kind,x.component_id))
