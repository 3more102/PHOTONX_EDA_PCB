from photonx_eda_pcb.quality_gate.parser_gate import parser_findings

def test_silent_parser_drop_is_gate_error():
    f=parser_findings([{'severity':'warning','code':'SILENT_DROP'}])
    assert f and f[0].severity=='error'
