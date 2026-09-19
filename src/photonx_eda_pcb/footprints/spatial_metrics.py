from photonx_eda_pcb.spatial_connectivity.points import build_point_index,radius_queries

def clustering_candidate_metrics(pads,max_gap_mm=5.0,cell_size_mm=None):
    pads=list(pads);n=len(pads);total=n*(n-1)//2
    if n<2:return {"bruteforce_pairs":total,"spatial_neighbor_pairs":0,"reduction_ratio":0.0}
    idx=build_point_index(((p.id,p) for p in pads),lambda p:(p.center.x,p.center.y),float(cell_size_mm or max(1.0,max_gap_mm)))
    seen=set()
    for p in pads:
        for _,nid in radius_query(idx,p.center.x,p.center.y,max_gap_mm):
            if nid!=p.id:seen.add(tuple(sorted((p.id,nid))))
    return {"bruteforce_pairs":total,"spatial_neighbor_pairs":len(seen),"reduction_ratio":round(1-len(seen)/total,6) if total else 0.0}
