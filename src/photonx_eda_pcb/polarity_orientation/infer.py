from .model import PolarityCandidate,OrientationCandidate
from .pin_names import polarity_from_pin_names
def infer_polarity(component_id,pins,marking=None):
    pos,neg=polarity_from_pin_names(pins);score=0.0;ev=[]
    if pos or neg:score+=.7;ev.append("pin_names")
    if marking:score+=.15;ev.append("body_marking")
    return PolarityCandidate(str(component_id),pos,neg,round(min(score,1),12),tuple(ev))
def infer_orientation(component_id,rotation_deg,pin1=None,placement_source=False):
    score=.9 if placement_source else (.55 if pin1 is not None else .3)
    ev=("placement",) if placement_source else (("pin1_geometry",) if pin1 is not None else ("package_axis",))
    return OrientationCandidate(str(component_id),float(rotation_deg)%360,None if pin1 is None else str(pin1),score,ev)
