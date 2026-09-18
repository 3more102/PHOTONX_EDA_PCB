import networkx as nx
from .model import SubgraphFingerprint
from .hashing import topology_hash,semantic_hash
from .features import extract_features
def fingerprint_subgraph(graph,nodes,seed="",radius=0,identity_by_id=None,roles_by_net=None):
    ordered=tuple(sorted(map(str,nodes)));sub=graph.subgraph(ordered).copy()
    features=extract_features(graph,ordered,identity_by_id,roles_by_net)
    semantic_known=sum(v for k,v in features.component_kinds if k!="unknown")
    total=sum(v for _,v in features.component_kinds)
    conf=1.0 if total==0 else round(.6+.4*(semantic_known/total),6)
    return SubgraphFingerprint(str(seed),int(radius),topology_hash(sub),semantic_hash(sub,identity_by_id,roles_by_net),features,ordered,conf)
def fingerprint_around_component(graph,component_id,radius=2,identity_by_id=None,roles_by_net=None):
    seed="C:"+str(component_id)
    if seed not in graph:raise KeyError(component_id)
    lengths=nx.single_source_shortest_path_length(graph,seed,cutoff=int(radius))
    return fingerprint_subgraph(graph,lengths.keys(),str(component_id),radius,identity_by_id,roles_by_net)
