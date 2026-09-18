from photonx_eda_pcb.real_board_corpus import CorpusCase,CorpusRegistry,compare_metrics,validate_case
def test_corpus_case():
    c=CorpusCase("board1",["a.gbr"],{"pads":10})
    r=CorpusRegistry();r.add(c)
    assert r.ids()==["board1"]
    assert compare_metrics({"pads":10},{"pads":10})["pads"]["status"]=="pass"
    assert validate_case(c)==[]
