from photonx_eda_pcb.board_statistics.model import BoardStats
from photonx_eda_pcb.board_statistics.history import StatsHistory
from photonx_eda_pcb.board_statistics.diff import diff_stats
def test_stats_history_and_diff():
    a=BoardStats(1,1,0,4,1,1,2.0,10,5);b=BoardStats(2,1,0,4,1,1,3.0,10,5)
    h=StatsHistory();h.add("a",a);h.add("b",b)
    assert h.latest()[0]=="b" and diff_stats(a,b)["tracks"]==(1,2)
