from photonx_eda_pcb.mechanical_features import SlotFeature
from photonx_eda_pcb.mechanical_features.geometry import slot_shape
from photonx_eda_pcb.mechanical_features.clearance import clearance_to_objects
from photonx_eda_pcb.models import PadCandidate,Point
from photonx_eda_pcb.geometry_kernel import object_shape
def test_slot_to_copper_spatial_matches_bruteforce():
    slot=slot_shape(SlotFeature("S",(0,0),(4,0),1))
    objs=[PadCandidate("A",Point(2,1),.5,.5,"C","F.Cu"),PadCandidate("B",Point(10,10),.5,.5,"C","F.Cu")]
    a=clearance_to_objects(slot,objs,object_shape,.3,use_spatial_index=False)
    b=clearance_to_objects(slot,objs,object_shape,.3,use_spatial_index=True)
    assert a==b==[("A",.25)]
