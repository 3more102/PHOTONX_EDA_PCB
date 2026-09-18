def outgoing(graph,node_id):return [e for e in graph.edges if e.source==node_id]
def incoming(graph,node_id):return [e for e in graph.edges if e.target==node_id]
def neighbors(graph,node_id):return sorted({e.target for e in outgoing(graph,node_id)}|{e.source for e in incoming(graph,node_id)})
