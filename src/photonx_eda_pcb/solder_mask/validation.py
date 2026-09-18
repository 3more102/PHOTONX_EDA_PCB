def validate_mask_openings(openings):
    issues=[]
    seen=set()
    for o in openings:
        if o.id in seen:issues.append("MASK_DUPLICATE_ID")
        seen.add(o.id)
        if o.size[0]<=0 or o.size[1]<=0:issues.append("MASK_NONPOSITIVE_SIZE")
    return issues
