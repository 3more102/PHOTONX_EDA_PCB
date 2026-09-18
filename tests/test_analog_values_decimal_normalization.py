from photonx_eda_pcb.analog_blocks.values import parse_resistance,parse_capacitance,parse_inductance

def test_scaled_analog_values_are_deterministic():
    assert parse_resistance("4.7K")==4700.0
    assert parse_capacitance("100nF")==1e-7
    assert parse_inductance("10uH")==1e-5
