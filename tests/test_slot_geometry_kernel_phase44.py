from photonx_eda_pcb.mechanical_features import SlotFeature
from photonx_eda_pcb.geometry_kernel import object_shape

def test_slot_supported_by_unified_geometry_kernel():
    s=SlotFeature("S",(0,0),(4,0),1.0,"non-plated")
    g=object_shape(s)
    assert g.bounds==(-.5,-.5,4.5,.5)
    assert round(g.area,6)>4.0
