def merge_candidates(primary,secondary):
    by={x.net_id:x for x in secondary}
    for x in primary:
        if x.net_id not in by or x.confidence>=by[x.net_id].confidence:by[x.net_id]=x
    return [by[k] for k in sorted(by)]
