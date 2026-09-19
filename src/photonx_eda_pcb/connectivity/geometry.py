from __future__ import annotations
from ..models import Track,PadCandidate,CopperRegion
from photonx_eda_pcb.geometry_kernel import track_shape,pad_shape,region_shape

def copper_shape(obj:Track|PadCandidate|CopperRegion):
    if isinstance(obj,Track):return track_shape(obj)
    if isinstance(obj,PadCandidate):return pad_shape(obj)
    if isinstance(obj,CopperRegion):return region_shape(obj)
    raise TypeError("unsupported copper object: "+type(obj).__name__)
