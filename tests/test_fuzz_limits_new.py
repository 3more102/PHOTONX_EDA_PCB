from photonx_eda_pcb.fuzzing.limits import within_limits

def test_fuzz_limits():
    assert within_limits('abc',10)
    assert not within_limits('abc',10001)
