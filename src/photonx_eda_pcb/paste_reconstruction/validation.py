def validate_paste(apertures):
    issues=[];seen=set()
    for a in apertures:
        if a.id in seen:issues.append("PASTE_DUPLICATE_ID")
        seen.add(a.id)
        if min(a.size)<=0:issues.append("PASTE_NONPOSITIVE_SIZE")
    return issues
