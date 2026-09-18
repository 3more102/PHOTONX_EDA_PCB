from .check import check_constraint
def check_all(constraints,estimates,confidences=None):
    confidences=confidences or {}
    return [check_constraint(c,estimates.get(c.net_id),confidences.get(c.net_id,1.0)) for c in constraints]
