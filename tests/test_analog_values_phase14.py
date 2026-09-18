from photonx_eda_pcb.analog_blocks.values import parse_resistance,parse_capacitance,parse_inductance
def test_value_parsers():
    assert parse_resistance("10kΩ")==10000
    assert parse_capacitance("100nF")==100e-9
    assert parse_inductance("10uH")==10e-6
