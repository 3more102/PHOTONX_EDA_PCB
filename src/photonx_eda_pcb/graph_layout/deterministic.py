from collections import deque
from .model import LayoutPosition,LayoutResult
def layout_components(graph,component_ids=None,x_step=30.0,y_step=20.0):
    comps=sorted(component_ids or [n[2:] for n in graph.nodes if str(n).startswith("C:")])
    comp_nodes={"C:"+c for c in comps};layers={};seen=set()
    roots=sorted(comp_nodes,key=lambda n:(graph.degree(n),n))
    for root in roots:
        if root in seen:continue
        q=deque([(root,0)]);seen.add(root)
        while q:
            node,depth=q.popleft();layers[node]=min(depth,layers.get(node,depth))
            neigh=[]
            for net in sorted(graph.neighbors(node)):
                if not str(net).startswith("N:"):continue
                for other in sorted(graph.neighbors(net)):
                    if other in comp_nodes and other not in seen:neigh.append(other)
            for other in neigh:
                seen.add(other);q.append((other,depth+1))
    buckets={}
    for n in sorted(comp_nodes):buckets.setdefault(layers.get(n,0),[]).append(n)
    pos={}
    for layer,nodes in sorted(buckets.items()):
        for row,n in enumerate(nodes):
            cid=n[2:];pos[cid]=LayoutPosition(cid,layer*float(x_step),row*float(y_step),layer)
    w=(max(buckets)+1)*float(x_step) if buckets else 0;h=max((len(v) for v in buckets.values()),default=0)*float(y_step)
    return LayoutResult(pos,w,h)
