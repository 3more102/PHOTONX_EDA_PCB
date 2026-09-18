def cross_partition_nets(partitions):
    owners={}
    for p in partitions:
        for n in p.net_ids:owners.setdefault(n,[]).append(p.id)
    return {n:tuple(sorted(v)) for n,v in owners.items() if len(v)>1}
