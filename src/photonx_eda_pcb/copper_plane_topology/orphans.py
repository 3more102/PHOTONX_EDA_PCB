def orphan_islands(topology,min_area_mm2=.01):
    return sorted(i.id for i in topology.islands if i.area_mm2>=min_area_mm2 and not topology.adjacency.get(i.id))
