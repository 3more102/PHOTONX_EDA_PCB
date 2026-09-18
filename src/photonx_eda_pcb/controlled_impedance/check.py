from .model import ImpedanceCheck
def check_constraint(constraint,estimate_ohms,confidence=1.0):
    if estimate_ohms is None:return ImpedanceCheck(constraint.net_id,None,constraint.target_ohms,None,None,float(confidence))
    err=abs(float(estimate_ohms)-float(constraint.target_ohms))
    return ImpedanceCheck(constraint.net_id,float(estimate_ohms),float(constraint.target_ohms),err,err<=float(constraint.tolerance_ohms),float(confidence))
