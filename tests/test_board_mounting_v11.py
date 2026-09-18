from photonx_eda_pcb.board_fit.mounting import match_mounting_holes
def test_mounting_hole_match():
    m=match_mounting_holes([(1,1),(9,9)],[(1.1,1),(8.9,9)],.2)
    assert len(m)==2
