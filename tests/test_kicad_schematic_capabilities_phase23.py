from photonx_eda_pcb.kicad_schematic_export.capabilities import export_capabilities
def test_export_capabilities_are_conservative():
    c=export_capabilities()
    assert c["wires"] and c["symbol_instances"] and not c["hierarchical_sheets"] and not c["native_kicad_cli_validation"]
