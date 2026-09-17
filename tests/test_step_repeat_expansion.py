from photonx_eda_pcb.gerber_geometry.step_repeat import offsets
def test_offsets(): assert offsets(2,2,1,3)==[(0,0),(1,0),(0,3),(1,3)]
