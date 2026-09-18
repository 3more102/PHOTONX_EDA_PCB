from .model import McuInterface
from photonx_eda_pcb.peripheral_mapping.graph import pins_on_nets
def build_mcu_interfaces(pmap,schematic_graph):
    out=[]
    for b in pmap.bindings:
        if b.role!="controller":continue
        pins=pins_on_nets(schematic_graph,b.component_id,b.nets)
        out.append(McuInterface(b.component_id,b.protocol,b.nets,pins,b.peer_components,b.confidence))
    return sorted(out,key=lambda x:(x.component_id,x.protocol))
