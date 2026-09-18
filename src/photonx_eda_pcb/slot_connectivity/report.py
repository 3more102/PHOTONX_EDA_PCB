def slot_connectivity_report(items):
    return [{"slot_id":x.slot_id,"layers":list(x.layers),"pad_ids":list(x.pad_ids),"net_ids":list(x.net_ids),"proven":x.proven,"conflict":x.conflict,"confidence":x.confidence,"evidence":list(x.evidence)} for x in items]
