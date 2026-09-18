from photonx_eda_pcb.board_fit import analyze_board_fit,validate_board_fit
def test_board_fits_enclosure():
    x=analyze_board_fit((1,1,9,9),(0,0,10,10),.9)
    assert x.fits and x.edge_margins==(1.0,1.0,1.0,1.0)
    assert validate_board_fit(x)==[]
def test_board_does_not_fit():
    assert not analyze_board_fit((0,0,11,10),(0,0,10,10)).fits
