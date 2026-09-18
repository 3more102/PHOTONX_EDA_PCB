from photonx_eda_pcb.pipeline import reconstruct
def test_pipeline_collects_routes(tmp_path):
    p=tmp_path/"board.drl"
    p.write_text("M48\nMETRIC\nT01C0.8\n%\nT01\nG00X1Y1\nM15\nG01X2Y1\nM16\nM30\n")
    result=reconstruct(tmp_path)
    assert len(result.board.routes)==1
