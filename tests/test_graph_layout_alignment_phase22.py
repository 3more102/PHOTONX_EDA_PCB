from photonx_eda_pcb.graph_layout.model import LayoutResult,LayoutPosition
from photonx_eda_pcb.graph_layout.align import align_group
def test_align_group():
    l=LayoutResult({"A":LayoutPosition("A",0,5),"B":LayoutPosition("B",10,6)})
    align_group(l,["B","A"],"y",20)
    assert l.positions["A"].y==0 and l.positions["B"].y==20
