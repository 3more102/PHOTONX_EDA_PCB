from photonx_eda_pcb.power_tree.voltage import parse_voltage
def test_voltage_formats():
    assert parse_voltage("+3V3")==3.3
    assert parse_voltage("5V")==5.0
    assert parse_voltage("-5V")==-5.0
