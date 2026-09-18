from photonx_eda_pcb.regression_corpus import Corpus,CorpusCase,CorpusExpectation,run_corpus,validate_corpus
from photonx_eda_pcb.regression_corpus.report import corpus_results_summary
def test_regression_corpus_runner():
    c=Corpus([CorpusCase("linear","parser",("top.gbr",),CorpusExpectation({"pads":2,"tracks":1}),True,"",("gerber",))])
    assert validate_corpus(c)==[]
    results=run_corpus(c,lambda case:{"pads":2,"tracks":1})
    assert results[0].passed and corpus_results_summary(results)["pass_rate"]==1.0
