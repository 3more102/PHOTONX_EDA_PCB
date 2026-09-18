from photonx_eda_pcb.kicad_schematic_roundtrip.canonical import canonical_schematic
from photonx_eda_pcb.kicad_schematic_roundtrip.compare import compare_schematics
from photonx_eda_pcb.kicad_schematic_roundtrip.fingerprint import schematic_fingerprint
def test_canonical_ignores_uuids_and_order():
    a={"version":1,"generator":"x","symbols":[{"lib_id":"D:R","reference":"R1","value":"1k","footprint":"","x":1.00001,"y":2,"rotation":0,"uuid":"a"}],"wires":[],"labels":[],"global_labels":[]}
    b={"version":1,"generator":"x","symbols":[{"lib_id":"D:R","reference":"R1","value":"1k","footprint":"","x":1.00002,"y":2,"rotation":0,"uuid":"b"}],"wires":[],"labels":[],"global_labels":[]}
    assert canonical_schematic(a)==canonical_schematic(b)
    assert compare_schematics(a,b)==[] and schematic_fingerprint(a)==schematic_fingerprint(b)
