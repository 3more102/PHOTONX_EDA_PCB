from photonx_eda_pcb.real_board_corpus.case import CorpusCase
from photonx_eda_pcb.real_board_corpus.runner import evaluate_case
def test_evaluate_case():
    c=CorpusCase("x",["a"],{"nets":3})
    assert evaluate_case(c,{"nets":3}).passed is True
