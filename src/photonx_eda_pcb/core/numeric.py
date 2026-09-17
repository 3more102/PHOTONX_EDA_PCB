import math
def is_finite_number(value)->bool:
    return isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value)
def require_positive(value:float, name:str="value")->float:
    if not is_finite_number(value) or value<=0: raise ValueError(f"{name} must be finite and > 0")
    return float(value)
