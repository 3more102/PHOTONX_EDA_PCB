def debug_connectors(candidate,component_kinds):
    return sorted(c for c in candidate.components if "connector" in str(component_kinds.get(c,"")).lower())
