def sort_islands(zone):
    zone.islands.sort(key=lambda i:i.id)
    return zone

def island_ids(zone):return [i.id for i in zone.islands]
