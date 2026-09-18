from photonx_eda_pcb.excellon_routing import RoutedPath,assess_route_export_readiness
def test_arbitrary_routes_are_explicitly_omitted():
    r=assess_route_export_readiness([RoutedPath("r",((0,0),(1,0),(1,1)),.5)])
    assert r.exportable==() and r.omitted==("r",)
    assert r.reasons["r"]=="KICAD_ARBITRARY_ROUTE_UNSUPPORTED"
