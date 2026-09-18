from photonx_eda_pcb.reference_designators.ranges import reference_range
def test_reference_range():
    assert reference_range(["R1","R4","R2"])==("R",1,4)
    assert reference_range(["R1","C1"]) is None
