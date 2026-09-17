from photonx_eda_pcb.gerber_geometry.macro_expr import evaluate
def test_expr(): assert evaluate('v1*2+3',{'v1':4})==11
