from .model import HierarchyBlock,HierarchyResult
from .features import block_key
def infer_hierarchy(graph):
    groups={}
    comp_nets={cid:set() for cid in graph.components}
    for cid,pin,nid in graph.pin_edges:
        comp_nets.setdefault(cid,set()).add(nid)
    for cid,node in graph.components.items():
        key=block_key(node.kind,comp_nets.get(cid,()))
        groups.setdefault(key,[]).append(cid)
    blocks=[]
    for key,cids in sorted(groups.items()):
        nets=sorted({n for c,p,n in graph.pin_edges if c in cids})
        conf=.7 if len(cids)>=2 else .5
        blocks.append(HierarchyBlock("block:"+key,key,sorted(cids),nets,conf,["kind_and_connectivity"]))
    return HierarchyResult(blocks,[])
