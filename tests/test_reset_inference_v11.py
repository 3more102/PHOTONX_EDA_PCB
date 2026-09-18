from photonx_eda_pcb.reset_inference import infer_reset_nets,validate_reset
from photonx_eda_pcb.reset_inference.polarity import polarity_label
def test_active_low_reset():
    r=infer_reset_nets([{"net_id":"r","label":"RESET_N","fanout":5}])[0]
    assert r.active_low is True and r.confidence>=.9
    assert polarity_label(r)=="active_low" and validate_reset(r)==[]
