def variant_placements(placements,variant):
    return [p for p in placements if variant.components.get(p.reference) is None or variant.components[p.reference].fitted]
