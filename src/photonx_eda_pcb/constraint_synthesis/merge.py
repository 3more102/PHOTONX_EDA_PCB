from .model import ConstraintSet
def merge_constraint_sets(*sets):
    by={}
    for s in sets:
        for c in s.constraints:
            if c.net_id not in by or c.confidence>by[c.net_id].confidence:by[c.net_id]=c
    return ConstraintSet([by[k] for k in sorted(by)])
