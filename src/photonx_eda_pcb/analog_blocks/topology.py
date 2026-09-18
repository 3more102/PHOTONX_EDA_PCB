def nets_for(component_id,component_pin_nets):
    return tuple(sorted({str(n) for n in component_pin_nets.get(component_id,{}).values() if n is not None}))
def shared_nets(a,b,component_pin_nets):
    return tuple(sorted(set(nets_for(a,component_pin_nets))&set(nets_for(b,component_pin_nets))))
def components_on_net(net_id,component_pin_nets):
    n=str(net_id)
    return sorted(cid for cid,pins in component_pin_nets.items() if n in {str(x) for x in pins.values() if x is not None})
