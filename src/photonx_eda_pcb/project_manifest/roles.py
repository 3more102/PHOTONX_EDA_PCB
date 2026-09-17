KNOWN_ROLES={"top_copper","bottom_copper","inner_copper","solder_mask","silkscreen","outline","drill","ipc356","bom","pick_place","image","unknown"}
def normalize_role(role):
    value=str(role).strip().lower().replace(" ","_")
    return value if value in KNOWN_ROLES else "unknown"
