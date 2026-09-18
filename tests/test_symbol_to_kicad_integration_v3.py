from photonx_eda_pcb.schematic_symbols import infer_symbol
from photonx_eda_pcb.kicad_schematic.from_hypotheses import schematic_from_hypotheses
from photonx_eda_pcb.kicad_schematic import write_schematic
def test_symbol_to_kicad():
    syms=[infer_symbol("R1","resistor",2),infer_symbol("LED1","led",2)]
    sch=schematic_from_hypotheses(syms,{"R1":"330Ω","LED1":"LED"})
    text=write_schematic(sch)
    assert '"R1"' in text and '"LED1"' in text and "Device:R" in text
