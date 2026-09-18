from .model import ProvenanceGraph
def merge_graphs(*graphs):
    out=ProvenanceGraph();seen=set()
    for g in graphs:
        out.nodes.update(g.nodes)
        for e in g.edges:
            key=(e.source,e.target,e.relation,e.confidence)
            if key not in seen:seen.add(key);out.edges.append(e)
    return out
