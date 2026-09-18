from photonx_eda_pcb.models import BoardModel
from photonx_eda_pcb.excellon_routing import RoutedPath
def test_board_model_indexes_and_serializes_routes():
    r=RoutedPath("r",((0,0),(1,0)),.5)
    b=BoardModel(routes=[r])
    assert b.object_index()["r"] is r
    assert b.to_dict()["routes"][0]["id"]=="r"
