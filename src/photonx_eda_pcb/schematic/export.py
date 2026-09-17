def export_connectivity_text(board)->str:
    lines=['# PHOTONX physical connectivity netlist','# This is not an original schematic.']
    for n in sorted(board.nets,key=lambda x:x.id):lines.append(n.id+': '+', '.join(sorted(n.members)))
    return '\n'.join(lines)+'\n'
