from .model import FingerprintFeatures
from .canonical import canonical_kind_counts
def extract_features(graph,nodes,identity_by_id=None,roles_by_net=None):
    comps=[n for n in nodes if str(n).startswith("C:")];nets=[n for n in nodes if str(n).startswith("N:")]
    component_degrees=tuple(sorted(int(graph.degree(n)) for n in comps))
    net_degrees=tuple(sorted(int(graph.degree(n)) for n in nets))
    roles=tuple(sorted({r for n in nets for r in (roles_by_net or {}).get(str(n)[2:],())}))
    return FingerprintFeatures(canonical_kind_counts(graph,nodes,identity_by_id),component_degrees,net_degrees,roles,int(graph.subgraph(nodes).number_of_edges()))
