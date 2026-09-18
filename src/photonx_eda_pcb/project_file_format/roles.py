KNOWN_ROLES={"gerber_copper","gerber_mask","gerber_silk","gerber_outline","excellon","ipc356","bom","pick_place","kicad_pcb","kicad_schematic","report","fixture"}
def role_known(role):return str(role) in KNOWN_ROLES
