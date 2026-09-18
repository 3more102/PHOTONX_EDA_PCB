from .model import SchematicGraph,ComponentNode,NetNode
def build_schematic_graph(netlist,component_kinds=None):
    kinds=component_kinds or {};g=SchematicGraph()
    for net_id,connections in netlist.nets.items():
        g.nets[net_id]=NetNode(net_id,netlist.labels.get(net_id))
        for c in connections:
            g.components.setdefault(c.component_id,ComponentNode(c.component_id,kinds.get(c.component_id,"unknown")))
            g.pin_edges.append((c.component_id,c.pin_id,net_id))
    g.pin_edges.sort()
    return g
