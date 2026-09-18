from photonx_eda_pcb.stress_harness.generators import grid_points,chain_edges
def test_stress_generators():
    assert len(grid_points(3))==9
    assert chain_edges(4)==[("0","1"),("1","2"),("2","3")]
