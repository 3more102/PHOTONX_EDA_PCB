from photonx_eda_pcb.kicad_reader.sexpr import parse_sexpr
def test_sexpr(): assert parse_sexpr('(a (b 1) "x")')==['a',['b',1],'x']
