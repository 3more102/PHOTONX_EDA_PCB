from .model import Endpoint,SerialLink
from .signatures import signal_role
from .pins import endpoints_for_net
def infer_serial_links(labels,schematic_graph):
    by_proto={}
    for net_id,label in labels.items():
        sr=signal_role(label)
        if sr is None:continue
        proto,role=sr;by_proto.setdefault(proto,[]).append((str(net_id),role))
    out=[]
    for proto,items in sorted(by_proto.items()):
        nets=tuple(sorted(n for n,_ in items));eps=[];roles=set()
        for n,role in items:
            roles.add(role)
            eps.extend(Endpoint(cid,pin,role) for cid,pin,_ in endpoints_for_net(schematic_graph,n,role))
        min_roles=2
        score=.55+(.15 if len(roles)>=min_roles else 0)+(.15 if len({e.component_id for e in eps})>=2 else 0)
        out.append(SerialLink(proto,nets,tuple(sorted(eps,key=lambda x:(x.component_id,x.pin or "",x.role))),round(min(score,1),12),("net_labels","schematic_endpoints")))
    return out
