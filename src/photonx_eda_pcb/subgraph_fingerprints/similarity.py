def _multiset_similarity(a,b):
    a=list(a);b=list(b)
    if not a and not b:return 1.0
    from collections import Counter
    ca,cb=Counter(a),Counter(b);keys=set(ca)|set(cb)
    inter=sum(min(ca[k],cb[k]) for k in keys);union=sum(max(ca[k],cb[k]) for k in keys)
    return inter/max(1,union)
def fingerprint_similarity(a,b):
    exact_topology=1.0 if a.topology_hash==b.topology_hash else 0.0
    exact_semantic=1.0 if a.semantic_hash==b.semantic_hash else 0.0
    kinds=_multiset_similarity(a.features.component_kinds,b.features.component_kinds)
    cdeg=_multiset_similarity(a.features.component_degrees,b.features.component_degrees)
    ndeg=_multiset_similarity(a.features.net_degrees,b.features.net_degrees)
    roles=_multiset_similarity(a.features.net_roles,b.features.net_roles)
    score=.25*exact_topology+.25*exact_semantic+.2*kinds+.12*cdeg+.1*ndeg+.08*roles
    return round(min(score,1.0),6)
