from .labels import classify_ddr_label
def group_ddr_nets(labels):
    groups={}
    for net_id,label in labels.items():
        role=classify_ddr_label(label)
        if role:groups.setdefault(role,[]).append(str(net_id))
    return {k:tuple(sorted(v)) for k,v in sorted(groups.items())}
