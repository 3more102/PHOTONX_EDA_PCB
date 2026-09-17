from dataclasses import dataclass
from photonx_eda_pcb.board_diff.engine import diff_collections
from photonx_eda_pcb.board_diff.summary import diff_summary

@dataclass(frozen=True)
class O:id:str; value:int

def test_board_diff_counts():
    d=diff_collections([O('a',1),O('b',2)],[O('b',3),O('c',4)])
    assert diff_summary(d)=={'total':3,'added':1,'removed':1,'changed':1}
