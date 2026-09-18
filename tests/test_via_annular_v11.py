from photonx_eda_pcb.via_transition.annular import annular_ring_mm
def test_annular_ring():
    assert annular_ring_mm(.7,.3)==.2
