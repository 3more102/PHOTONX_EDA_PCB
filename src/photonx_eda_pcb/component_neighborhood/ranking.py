def nearest_matches(target,candidates):
    from .similarity import neighborhood_similarity
    return sorted([(neighborhood_similarity(target,c),c.component_id) for c in candidates if c.component_id!=target.component_id],key=lambda x:(-x[0],x[1]))
