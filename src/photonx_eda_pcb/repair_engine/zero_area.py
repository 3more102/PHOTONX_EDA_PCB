from .candidate import RepairCandidate
def zero_area_candidate(object_id,area,epsilon=1e-12):
    if abs(area)>epsilon:return None
    return RepairCandidate('remove_zero_area',(object_id,),1.0,'geometry has zero measurable area',True,{'area':area})
