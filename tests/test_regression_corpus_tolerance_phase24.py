from photonx_eda_pcb.regression_corpus.model import CorpusCase,CorpusExpectation
from photonx_eda_pcb.regression_corpus.runner import run_case
def test_corpus_numeric_tolerance():
    c=CorpusCase("x","geometry",("x",),CorpusExpectation({"width":1.0},{"width":.05}))
    assert run_case(c,lambda _:{"width":1.03}).passed
