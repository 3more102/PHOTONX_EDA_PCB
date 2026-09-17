def best_candidate(candidates):
    items=list(candidates)
    if not items:return None
    return sorted(items,key=lambda item:(-item.confidence,item.name,item.source))[0]
