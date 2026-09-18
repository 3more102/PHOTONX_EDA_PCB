def inter_block_nets(result):
    memberships={}
    for b in result.blocks:
        for n in b.net_ids:memberships.setdefault(n,[]).append(b.id)
    return {n:sorted(v) for n,v in memberships.items() if len(set(v))>1}
