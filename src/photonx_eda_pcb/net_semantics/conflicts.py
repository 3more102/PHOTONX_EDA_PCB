from collections import defaultdict
def conflicting_names(candidates,min_confidence=0.5):
    names=defaultdict(set)
    for candidate in candidates:
        if candidate.confidence>=min_confidence:names[candidate.net_id].add(candidate.name)
    return {net_id:tuple(sorted(values)) for net_id,values in sorted(names.items()) if len(values)>1}
