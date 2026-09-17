from .candidate import RepairCandidate
def self_touch_candidate(object_id,touch_points):
    pts=list(touch_points)
    if not pts:return None
    return RepairCandidate('review_self_touch',(object_id,),0.8,f'{len(pts)} self-touch point(s) detected',False,{'points':pts})
