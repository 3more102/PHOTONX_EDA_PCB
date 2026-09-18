from photonx_eda_pcb.kicad_schematic import KicadSchematic,KicadSymbol
from photonx_eda_pcb.kicad_schematic.determinism import schematic_sha256
def test_hash_stable():
    a=KicadSchematic([KicadSymbol("R2","1k","Device:R",0,0),KicadSymbol("R1","2k","Device:R",1,0)])
    b=KicadSchematic([KicadSymbol("R1","2k","Device:R",1,0),KicadSymbol("R2","1k","Device:R",0,0)])
    assert schematic_sha256(a)==schematic_sha256(b)
