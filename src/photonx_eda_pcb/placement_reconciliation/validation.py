def validate_placement_deltas(items):
    issues=[]
    for x in items:
        if x.distance_mm<0:issues.append("PLACEMENT_NEGATIVE_DISTANCE")
        if x.rotation_delta_deg<0 or x.rotation_delta_deg>180:issues.append("PLACEMENT_BAD_ROTATION_DELTA")
    return issues
