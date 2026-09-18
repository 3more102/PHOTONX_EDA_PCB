from photonx_eda_pcb.regression_corpus import Corpus,CorpusCase,CorpusExpectation
from photonx_eda_pcb.regression_corpus.fingerprint import corpus_fingerprint
def test_corpus_fingerprint_deterministic():
    a=Corpus([CorpusCase("b","parser",("b",),CorpusExpectation({"x":1})),CorpusCase("a","parser",("a",),CorpusExpectation({"x":1}))])
    b=Corpus(list(reversed(a.cases)))
    assert corpus_fingerprint(a)==corpus_fingerprint(b)
