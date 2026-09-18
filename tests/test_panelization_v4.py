from photonx_eda_pcb.panelization_evidence import infer_panel,validate_panel
def test_repeated_boards_panel():
    p=infer_panel([(0,0,10,5),(12,0,22,5)],[(1,1),(21,1)])
    assert len(p.boards)==2 and p.confidence>=.7
    assert validate_panel(p)==[]
