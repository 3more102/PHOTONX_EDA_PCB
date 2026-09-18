from .candidates import build_pad_candidate_index,pads_near_drill

def via_span_candidate_metrics(board,tolerance_mm=.15,cell_size_mm=None):
    total=len(board.pads)*len(board.drills)
    if not board.pads or not board.drills:return {"bruteforce_pairs":total,"spatial_candidates":0,"reduction_ratio":1.0 if total else 0.0}
    idx,by=build_pad_candidate_index(board,tolerance_mm,cell_size_mm)
    candidates=sum(len(pads_near_drill(board,d,tolerance_mm,index=idx,pad_by_id=by)) for d in board.drills)
    return {"bruteforce_pairs":total,"spatial_candidates":candidates,"reduction_ratio":round(1-candidates/total,6) if total else 0.0}
