from photonx_eda_pcb.length_analysis.meanders import excess_length
def test_excess_length():
    assert excess_length([(0,0),(1,1),(2,0)])>0
