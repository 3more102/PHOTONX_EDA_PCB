def termination_coverage(candidates,critical_nets):
    nets={n for c in candidates for n in c.nets};crit=set(map(str,critical_nets))
    return 1.0 if not crit else round(len(nets&crit)/len(crit),6)
