import networkx as nx
from .model import SignalPath
def _node(name):return name if str(name).startswith(("C:","N:")) else "C:"+str(name)
def trace_path(graph,start,end):
    try:nodes=tuple(nx.shortest_path(graph,_node(start),_node(end)))
    except (nx.NetworkXNoPath,nx.NodeNotFound):return None
    return SignalPath(nodes,max(0,len(nodes)-1),1.0)
def all_paths_between(graph,start,end,cutoff=12,max_paths=100):
    try:paths=nx.all_simple_paths(graph,_node(start),_node(end),cutoff=cutoff)
    except (nx.NodeNotFound,nx.NetworkXNoPath):return []
    out=[]
    for p in paths:
        out.append(SignalPath(tuple(p),len(p)-1,1.0))
        if len(out)>=max_paths:break
    return out
