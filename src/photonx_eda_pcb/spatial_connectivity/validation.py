def validate_index(index):
    issues=[]
    for oid,b in index._boxes.items():
        if b.min_x>b.max_x or b.min_y>b.max_y:issues.append("SPATIAL_INVALID_BOUNDS")
    return issues
