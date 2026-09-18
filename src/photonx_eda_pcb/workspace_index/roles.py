ROLE_GROUPS={"manufacturing":{"gerber_copper","gerber_mask","gerber_silk","gerber_outline","excellon","ipc356"},"assembly":{"bom","pick_place"},"design":{"kicad_pcb","kicad_schematic"},"output":{"report","export"}}
def role_group(role):
    for name,items in ROLE_GROUPS.items():
        if role in items:return name
    return "other"
