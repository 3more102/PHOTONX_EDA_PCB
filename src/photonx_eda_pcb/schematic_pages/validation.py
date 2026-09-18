def validate_page_set(ps):
    issues=[];ids=set()
    for p in ps.pages:
        if p.id in ids:issues.append("SCHEMATIC_PAGE_DUPLICATE_ID")
        ids.add(p.id)
        if not p.components:issues.append("SCHEMATIC_PAGE_EMPTY")
    return issues
