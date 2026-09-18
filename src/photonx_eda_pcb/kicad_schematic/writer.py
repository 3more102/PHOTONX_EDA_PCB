from .escape import kicad_string
def write_schematic(schematic):
    lines=['(kicad_sch (version 20231120) (generator photonx)']
    for s in sorted(schematic.symbols,key=lambda x:x.reference):
        lines.append(f'  (symbol (lib_id {kicad_string(s.library_id)}) (at {s.x:.6f} {s.y:.6f} {s.rotation:.1f}) (property "Reference" {kicad_string(s.reference)}) (property "Value" {kicad_string(s.value)}))')
    for w in schematic.wires:
        lines.append(f'  (wire (pts (xy {w.start[0]:.6f} {w.start[1]:.6f}) (xy {w.end[0]:.6f} {w.end[1]:.6f})))')
    for text,x,y in schematic.labels:
        lines.append(f'  (label {kicad_string(text)} (at {x:.6f} {y:.6f} 0))')
    lines.append(')')
    return "\n".join(lines)+"\n"
