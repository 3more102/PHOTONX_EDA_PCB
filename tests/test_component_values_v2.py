from photonx_eda_pcb.component_values import decode_resistor_marking,decode_capacitor_code,infer_value
def test_value_codes():
    assert decode_resistor_marking("103")==10000
    assert decode_resistor_marking("4R7")==4.7
    assert round(decode_capacitor_code("104"),12)==round(100e-9,12)
    assert infer_value("R1","103","resistor").value=="10kΩ"
