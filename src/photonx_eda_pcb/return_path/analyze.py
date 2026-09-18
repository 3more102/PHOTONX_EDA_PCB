from .model import ReturnPathEvidence
from .continuity import continuity_score
from .vias import return_via_penalty
def analyze_return_path(net_id,*,plane=None,continuity_samples=(),signal_vias=0,return_vias=0,split_crossings=0):
    c=continuity_score(continuity_samples)
    vp=return_via_penalty(signal_vias,return_vias)
    ev=[]
    if plane:ev.append("reference_plane")
    if continuity_samples:ev.append("plane_continuity_samples")
    if signal_vias:ev.append("via_transition_evidence")
    confidence=min(1.0,(.35 if plane else 0)+(.4 if continuity_samples else 0)+(.25 if signal_vias or return_vias else 0))
    return ReturnPathEvidence(str(net_id),plane,c,vp,int(split_crossings),round(confidence,6),ev)
