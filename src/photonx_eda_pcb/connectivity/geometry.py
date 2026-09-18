from __future__ import annotations
from ..models import Track,PadCandidate
from photonx_eda_pcb.geometry_kernel import track_shape,pad_shape

def copper_shape(obj:Track|PadCandidate):
    if isinstance(obj,Track):return track_shape(obj)
    return pad_shape(obj)
