def reference_plane_candidates(topology,min_area_mm2=10.0):
    return sorted((i for i in topology.islands if i.area_mm2>=min_area_mm2),key=lambda i:(-i.area_mm2,i.id))
