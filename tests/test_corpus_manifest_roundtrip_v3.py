from photonx_eda_pcb.real_board_corpus.case import CorpusCase
from photonx_eda_pcb.real_board_corpus.manifest import dump_case_json,load_case_json
def test_corpus_manifest_roundtrip():
    a=CorpusCase("x",["a.gbr"],{"pads":5},{"GND":["P1"]},"note")
    b=load_case_json(dump_case_json(a))
    assert b==a
