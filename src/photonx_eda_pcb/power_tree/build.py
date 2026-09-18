from .model import PowerNode,PowerEdge,PowerTree
from .voltage import parse_voltage
from .sources import is_power_source_kind
def build_power_tree(graph,power_nets):
    p=set(map(str,power_nets));tree=PowerTree()
    for nid in p:
        label=getattr(graph.nets.get(nid),"label",None)
        tree.nodes["N:"+nid]=PowerNode("N:"+nid,"net",parse_voltage(label))
    for cid,node in graph.components.items():
        touched={n for c,pin,n in graph.pin_edges if c==cid and n in p}
        if touched:
            tree.nodes["C:"+cid]=PowerNode("C:"+cid,"source" if is_power_source_kind(node.kind) else "load",None)
            for n in sorted(touched):
                rel="drives" if is_power_source_kind(node.kind) else "consumes"
                tree.edges.append(PowerEdge("C:"+cid,"N:"+n,rel,.65))
    return tree
