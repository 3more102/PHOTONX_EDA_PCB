def merge_candidates(candidates):
    best={}
    for candidate in candidates:
        key=(candidate.net_id,candidate.name)
        if key not in best or candidate.confidence>best[key].confidence: best[key]=candidate
    return tuple(sorted(best.values(),key=lambda item:(item.net_id,-item.confidence,item.name)))
