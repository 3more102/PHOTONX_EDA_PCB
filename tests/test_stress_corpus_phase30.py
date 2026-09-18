from photonx_eda_pcb.stress_corpus import grid_board,clustered_board,board_size_metrics
from photonx_eda_pcb.stress_corpus.expected import grid_expected
def test_stress_board_sizes():
    b=grid_board(10,12);m=board_size_metrics(b);e=grid_expected(10,12)
    assert m["pads"]==e["pads"] and m["tracks"]==e["tracks"]
    c=clustered_board(3,10);assert len(c.pads)==30
