def zone_membership(zone,point_ids_by_island):
    out=set()
    for island in zone.islands:out.update(point_ids_by_island.get(island.id,()))
    return out

def isolated_islands(zone,point_ids_by_island):
    return [i.id for i in zone.islands if not point_ids_by_island.get(i.id)]
