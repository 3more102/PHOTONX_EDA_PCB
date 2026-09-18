def connector_candidates(component_kinds,pin_counts,min_pins=2):
    return sorted(cid for cid,k in component_kinds.items() if "connector" in str(k).lower() and int(pin_counts.get(cid,0))>=min_pins)
