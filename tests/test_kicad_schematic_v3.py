from photonx_eda_pcb.kicad_schematic import KicadSchematic,KicadSymbol,write_schematic,validate_schematic
def test_writer():
    s=KicadSchematic([KicadSymbol("R1","10k","Device:R",0,0)],[],[("GND",5,5)])
    text=write_schematic(s)
    assert text.startswith("(kicad_sch")
    assert '"R1"' in text and '"GND"' in text
    assert validate_schematic(s)==[]
