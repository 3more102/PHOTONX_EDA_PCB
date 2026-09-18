from photonx_eda_pcb.models import Track,PadCandidate,DrillHit
from .tracks import track_shape
from .pads import pad_shape
from .drills import drill_shape
def object_shape(obj):
    if isinstance(obj,Track):return track_shape(obj)
    if isinstance(obj,PadCandidate):return pad_shape(obj)
    if isinstance(obj,DrillHit):return drill_shape(obj)
    raise TypeError("unsupported geometry object: "+type(obj).__name__)
