def validate_layout(layout):
    issues=[];seen=set()
    for p in layout.positions.values():
        key=(p.x,p.y)
        if key in seen:issues.append("LAYOUT_POSITION_COLLISION")
        seen.add(key)
    return issues
