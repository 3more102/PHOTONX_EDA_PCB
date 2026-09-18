from photonx_eda_pcb.schematic_symbols.reference_prefix import infer_kind_from_reference
def test_reference_prefix():
    assert infer_kind_from_reference("R12")=="resistor"
    assert infer_kind_from_reference("LED3")=="led"
