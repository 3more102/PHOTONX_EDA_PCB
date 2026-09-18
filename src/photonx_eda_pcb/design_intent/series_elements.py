def series_element_candidates(component_kinds,pin_counts):
    return sorted(cid for cid,k in component_kinds.items() if int(pin_counts.get(cid,0))==2 and any(x in str(k).lower() for x in ("resistor","ferrite","inductor","fuse")))
