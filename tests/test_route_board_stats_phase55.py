from photonx_eda_pcb.models import BoardModel
from photonx_eda_pcb.excellon_routing import RoutedPath
from photonx_eda_pcb.analysis.board_stats import board_stats
def test_route_stats():
    s=board_stats(BoardModel(routes=[RoutedPath("r",((0,0),(3,4)),.5)]))
    assert s["routes"]==1 and s["route_length_mm"]==5.0
