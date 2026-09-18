from photonx_eda_pcb.current_capacity.derating import derated_current
def test_derating():
    assert derated_current(2,.8)==1.6
