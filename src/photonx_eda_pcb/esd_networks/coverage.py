def esd_coverage(items,interface_nets):
    covered={x.interface_net for x in items};alln=set(map(str,interface_nets))
    return 1.0 if not alln else round(len(covered&alln)/len(alln),6)
