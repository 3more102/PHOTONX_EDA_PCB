from .model import PeripheralBinding,PeripheralMap
from .classify import endpoint_role
from .graph import components_on_nets
def infer_peripheral_map(protocols,schematic_graph,identities=None):
    identities=identities or {};out=[]
    for p in protocols:
        comps=components_on_nets(schematic_graph,p.net_ids)
        for cid in comps:
            peers=tuple(x for x in comps if x!=cid)
            role=endpoint_role(cid,identities)
            score=float(p.confidence)
            if role=="controller":score=min(1.0,score+.1)
            if peers:score=min(1.0,score+.05)
            out.append(PeripheralBinding(cid,p.protocol,tuple(sorted(p.net_ids)),peers,role,round(score,12),tuple(sorted(set(p.evidence+("schematic_connectivity",))))))
    return PeripheralMap(sorted(out,key=lambda x:(x.component_id,x.protocol,x.nets)))
