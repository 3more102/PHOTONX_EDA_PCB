import networkx as nx
from .model import FunctionalBlock
from .classify import classify_block
def cluster_functional_blocks(graph,identity_by_id=None,roles_by_net=None):
    identity_by_id=identity_by_id or {};roles_by_net=roles_by_net or {};out=[]
    for i,nodes in enumerate(nx.connected_components(graph)):
        comps=sorted(x[2:] for x in nodes if str(x).startswith("C:"));nets=sorted(x[2:] for x in nodes if str(x).startswith("N:"))
        if not comps:continue
        kinds=[str(getattr(identity_by_id.get(c),"kind","unknown") or "unknown").lower() for c in comps]
        roles=sorted({r for n in nets for r in roles_by_net.get(n,())})
        kind=classify_block(kinds,roles)
        conf=.55+(.15 if kind!="unknown" else 0)+(.1 if roles else 0)
        out.append(FunctionalBlock(f"block:{i}",tuple(comps),tuple(nets),kind,round(min(conf,1),6),tuple(["connectivity_component"]+(["signal_roles"] if roles else []))))
    return out
