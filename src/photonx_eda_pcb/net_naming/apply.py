def apply_resolved_names(netlist,resolved):
    labels=dict(netlist.labels)
    for x in resolved:
        if x.name:labels[x.net_id]=x.name
    return type(netlist)(dict(netlist.nets),labels)
