import networkx as nx
from .model import ConnectorPath
def trace_connector_paths(graph,connectors,targets,max_hops=10):
    out=[]
    for c in sorted(map(str,connectors)):
        start="C:"+c
        if start not in graph:continue
        for t in sorted(map(str,targets)):
            end="C:"+t
            if end not in graph or end==start:continue
            try:p=nx.shortest_path(graph,start,end)
            except (nx.NetworkXNoPath,nx.NodeNotFound):continue
            hops=len(p)-1
            if hops<=max_hops:
                conf=round(max(.3,1-.05*hops),6)
                out.append(ConnectorPath(c,t,tuple(p),hops,conf))
    return sorted(out,key=lambda x:(x.connector_id,x.hops,x.target_id))
