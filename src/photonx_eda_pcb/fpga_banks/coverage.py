def bank_net_coverage(bank):
    return 1.0 if not bank.pins else round(sum(x.net_id is not None for x in bank.pins)/len(bank.pins),6)
