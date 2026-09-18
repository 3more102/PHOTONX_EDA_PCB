def protected_net_coverage(items,nets):
    protected={n for x in items for n in x.protected_nets};alln=set(map(str,nets))
    return 1.0 if not alln else round(len(protected&alln)/len(alln),6)
