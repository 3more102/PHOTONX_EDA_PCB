from photonx_eda_pcb.schematic_symbols import infer_symbol,validate_symbol
def test_resistor_symbol():
    s=infer_symbol("R1","resistor",2)
    assert s.library_id=="Device:R" and len(s.pins)==2
    assert validate_symbol(s)==[]
