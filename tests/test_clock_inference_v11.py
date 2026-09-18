from photonx_eda_pcb.clock_inference import infer_clock_nets,validate_clock
from photonx_eda_pcb.clock_inference.frequency import parse_frequency_hint
def test_clock_inference():
    c=infer_clock_nets([{"net_id":"n","label":"SYSCLK","fanout":8,"source_kind":"oscillator"}])[0]
    assert c.confidence==1.0 and validate_clock(c)==[]
    assert parse_frequency_hint("25 MHz")==25e6
