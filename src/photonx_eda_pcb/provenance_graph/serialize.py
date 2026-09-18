import json
def graph_json(graph):
    return json.dumps({"nodes":[{"id":n.id,"kind":n.kind,"label":n.label} for n in sorted(graph.nodes.values(),key=lambda x:x.id)],"edges":[{"source":e.source,"target":e.target,"relation":e.relation,"confidence":e.confidence} for e in sorted(graph.edges,key=lambda x:(x.source,x.target,x.relation))]},sort_keys=True,separators=(",",":"))
