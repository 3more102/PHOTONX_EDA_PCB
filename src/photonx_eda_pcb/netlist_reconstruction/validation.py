def validate_netlist(netlist):
    issues=[]; seen=set()
    for net_id,connections in netlist.nets.items():
        if not net_id:issues.append('NETLIST_NET_ID_EMPTY')
        for c in connections:
            key=(c.component_id,c.pin_id)
            if key in seen:issues.append('NETLIST_PIN_MULTIPLE_NETS')
            seen.add(key)
    return issues
