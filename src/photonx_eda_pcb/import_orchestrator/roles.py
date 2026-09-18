FORMAT_ROLES={"gerber":"manufacturing","excellon":"drill","ipc356":"electrical_test","kicad_pcb":"design_board","kicad_schematic":"design_schematic","csv":"tabular","json":"structured"}
def import_role(fmt):return FORMAT_ROLES.get(str(fmt),"unknown")
