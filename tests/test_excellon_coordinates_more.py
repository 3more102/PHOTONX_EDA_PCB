from photonx_eda_pcb.parsers.excellon_parts.coordinates import parse_excellon_xy
def test_xy(): assert parse_excellon_xy('X100Y200')=={'x':'100','y':'200'}
