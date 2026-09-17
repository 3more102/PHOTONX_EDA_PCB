from photonx_eda_pcb.fuzzing.corpus import CorpusCase
from photonx_eda_pcb.fuzzing.mutations import mutate_text
from photonx_eda_pcb.fuzzing.runner import run_fuzz_cases

def test_fuzz_runner_records_exceptions():
    cases=[CorpusCase('ok','1'),CorpusCase('bad','x')]
    r=run_fuzz_cases(cases,int)
    assert r[0]['status']=='ok' and r[1]['exception']=='ValueError'
    assert mutate_text('abc',1,'X')=='aXc'
