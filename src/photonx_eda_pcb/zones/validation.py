def validate_zone(zone):
    issues=[]
    if not zone.id:issues.append('ZONE_ID_EMPTY')
    if not zone.layer:issues.append('ZONE_LAYER_EMPTY')
    if zone.clearance_mm is not None and zone.clearance_mm<0:issues.append('ZONE_CLEARANCE_NEGATIVE')
    if zone.min_thickness_mm is not None and zone.min_thickness_mm<0:issues.append('ZONE_MIN_THICKNESS_NEGATIVE')
    seen=set()
    for island in zone.islands:
        if island.id in seen:issues.append('ZONE_ISLAND_DUPLICATE_ID')
        seen.add(island.id)
        if len(island.polygon)<3:issues.append('ZONE_ISLAND_TOO_SMALL')
    return issues
