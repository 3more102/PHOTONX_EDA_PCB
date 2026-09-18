from photonx_eda_pcb.polygon_boolean.normalize import normalize_polygon,signed_area
def test_normalize_is_ccw_and_stable():
    p=normalize_polygon(((1,1),(1,0),(0,0),(0,1),(1,1)))
    assert p[0]==(0.0,0.0)
    assert signed_area(p)>0
