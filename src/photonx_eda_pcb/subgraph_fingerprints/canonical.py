from collections import Counter
def component_kind(graph,node,identity_by_id=None):
    cid=str(node)[2:] if str(node).startswith("C:") else str(node)
    identity=(identity_by_id or {}).get(cid)
    kind=str(getattr(identity,"kind","") or graph.nodes[node].get("kind","unknown") or "unknown").lower()
    return kind
def canonical_node_label(graph,node,identity_by_id=None,roles_by_net=None):
    s=str(node)
    if s.startswith("C:"):return "C:"+component_kind(graph,node,identity_by_id)
    if s.startswith("N:"):
        nid=s[2:];roles=tuple(sorted((roles_by_net or {}).get(nid,())))
        return "N:"+(",".join(roles) if roles else "net")
    return "X:"+str(graph.nodes[node].get("kind","unknown"))
def canonical_kind_counts(graph,nodes,identity_by_id=None):
    c=Counter(component_kind(graph,n,identity_by_id) for n in nodes if str(n).startswith("C:"))
    return tuple(sorted(c.items()))
