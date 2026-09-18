from photonx_eda_pcb.models import Track,PadCandidate,DrillHit
from photonx_eda_pcb.mechanical_features.model import SlotFeature,MechanicalHole
from .tracks import track_shape
from .pads import pad_shape
from .drills import drill_shape
from photonx_eda_pcb.mechanical_features.geometry import slot_shape,hole_shape

def object_shape(obj):
    if isinstance(obj,Track):return track_shape(obj)
    if isinstance(obj,PadCandidate):return pad_shape(obj)
    if isinstance(obj,DrillHit):return drill_shape(obj)
    if isinstance(obj,SlotFeature):return slot_shape(obj)
    if isinstance(obj,MechanicalHole):return hole_shape(obj)
    raise TypeError("unsupported geometry object: "+type(obj).__name__)
