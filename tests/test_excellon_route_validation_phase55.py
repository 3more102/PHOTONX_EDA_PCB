from photonx_eda_pcb.excellon_routing import RoutedPath,validate_route
def test_route_validation():
    assert validate_route(RoutedPath("r",((0,0),(1,0)),.5))==[]
    bad=validate_route(RoutedPath("",((0,0),(0,0)),0))
    assert "ROUTE_ID_EMPTY" in bad and "ROUTE_WIDTH_NONPOSITIVE" in bad and "ROUTE_ZERO_LENGTH_SEGMENT" in bad
