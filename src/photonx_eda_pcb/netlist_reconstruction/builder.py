from .model import Netlist,NetConnection

def build_netlist(component_pin_nets,labels=None):
    nets={}
    for component_id,pins in component_pin_nets.items():
        for pin_id,net_id in pins.items():
            if net_id is None:continue
            nets.setdefault(str(net_id),[]).append(NetConnection(str(component_id),str(pin_id)))
    for v in nets.values():v.sort(key=lambda x:(x.component_id,x.pin_id))
    return Netlist(nets,dict(labels or {}))
