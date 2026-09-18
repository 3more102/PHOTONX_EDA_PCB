def protocol_coverage(items,total_nets):
    used=len({n for x in items for n in x.net_ids})
    return 0.0 if total_nets<=0 else round(used/total_nets,6)
