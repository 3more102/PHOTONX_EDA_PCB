from photonx_eda_pcb.mechanical_features import SlotFeature,slot_shape,validate_slot
def test_slot_capsule_geometry():
    s=SlotFeature("S",(0,0),(4,0),1.0)
    g=slot_shape(s)
    assert g.bounds==(-.5,-.5,4.5,.5)
    assert validate_slot(s)==[]
