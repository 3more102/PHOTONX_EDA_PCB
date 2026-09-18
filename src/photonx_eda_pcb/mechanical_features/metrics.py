def clearance_candidate_metrics(feature_shapes,objects,shape_fn,minimum_mm):
    from .spatial import nearby_object_ids
    objects=list(objects);total=len(feature_shapes)*len(objects);candidates=0
    for f in feature_shapes:candidates+=len(nearby_object_ids(f,objects,shape_fn,minimum_mm))
    return {"bruteforce_pairs":total,"spatial_candidates":candidates,"reduction_ratio":1.0 if total==0 else round(1-candidates/total,6)}
