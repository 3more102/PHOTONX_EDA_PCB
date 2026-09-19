from photonx_eda_pcb.spatial_connectivity.points import build_point_index,radius_queries

def drill_association_candidate_metrics(board,tolerance_mm=.15,cell_size_mm=None):
    total=len(board.pads)*len(board.drills)
    if not board.pads or not board.drills:return {"bruteforce_pairs":total,"spatial_candidates":0,"reduction_ratio":1.0 if total else 0.0}
    idx=build_point_index(((d.id,d) for d in board.drills),lambda d:(d.center.x,d.center.y),float(cell_size_mm or max(1.0,tolerance_mm*8)))
    candidates=sum(len(items) for items in radius_queries(idx,((p.center.x,p.center.y,tolerance_mm) for p in board.pads)))
    return {"bruteforce_pairs":total,"spatial_candidates":candidates,"reduction_ratio":round(1-candidates/total,6) if total else 0.0}
