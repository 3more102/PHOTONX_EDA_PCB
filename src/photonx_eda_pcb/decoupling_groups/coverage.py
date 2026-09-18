def group_coverage(groups,power_nets):
    covered={x.power_net for x in groups};alln=set(map(str,power_nets))
    return 1.0 if not alln else round(len(covered&alln)/len(alln),6)
