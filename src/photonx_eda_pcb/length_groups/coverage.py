def length_group_coverage(groups,critical_nets):
    grouped={n for g in groups for n in g.nets};crit=set(map(str,critical_nets))
    return 1.0 if not crit else round(len(grouped&crit)/len(crit),6)
