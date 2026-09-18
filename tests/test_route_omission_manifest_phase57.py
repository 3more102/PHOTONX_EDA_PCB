from photonx_eda_pcb.models import BoardModel
from photonx_eda_pcb.excellon_routing import RoutedPath
from photonx_eda_pcb.exporters.route_omissions import route_omission_manifest,validate_route_omission_manifest
def test_route_omission_manifest_has_reason():
    d=route_omission_manifest(BoardModel(routes=[RoutedPath("r",((0,0),(1,0)),.5)]))
    assert d["omitted_routes"]==["r"]
    assert validate_route_omission_manifest(d)==[]
