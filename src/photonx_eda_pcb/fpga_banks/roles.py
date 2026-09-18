def bank_roles(bank,roles_by_net):
    roles=set()
    for p in bank.pins:
        if p.net_id:roles.update(roles_by_net.get(p.net_id,()))
    return tuple(sorted(roles))
