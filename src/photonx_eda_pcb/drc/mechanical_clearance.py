from .model import DrcIssue
from photonx_eda_pcb.geometry_kernel import object_shape
from photonx_eda_pcb.mechanical_features.geometry import slot_shape,hole_shape
from photonx_eda_pcb.mechanical_features.clearance import clearance_to_objects

def check_mechanical_features(features,board,minimum_mm=.15):
    copper=[*board.tracks,*board.pads];out=[]
    for feature in features:
        shape=slot_shape(feature) if hasattr(feature,"width_mm") else hole_shape(feature)
        hits=clearance_to_objects(shape,copper,object_shape,minimum_mm)
        for oid,distance in hits:
            out.append(DrcIssue("error","MECHANICAL_COPPER_CLEARANCE",f"mechanical-feature clearance {distance:.6f} mm below {minimum_mm} mm",(feature.id,oid)))
    return sorted(out,key=lambda x:x.object_ids)
