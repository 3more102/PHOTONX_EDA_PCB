from photonx_eda_pcb.regression_corpus import Corpus,CorpusCase,CorpusExpectation,run_corpus
from photonx_eda_pcb.production_release_profiles import research_profile,ReleaseEvidence,evaluate_release_profile
def test_corpus_result_can_feed_release_decision():
    corpus=Corpus([CorpusCase("x","parser",("x",),CorpusExpectation({"count":1}))])
    results=run_corpus(corpus,lambda _:{"count":1})
    failures=sum(not x.passed for x in results)
    e=ReleaseEvidence({},{"provenance_coverage":.8,"completeness":.8},failures,True,True)
    assert evaluate_release_profile(research_profile(),e).passed
