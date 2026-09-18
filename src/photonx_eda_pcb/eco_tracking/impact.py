CATEGORY_IMPACT={"track":{"connectivity","length"},"pad":{"footprint","connectivity"},"net":{"schematic","electrical"},"component":{"assembly","bom"},"outline":{"mechanical"}}
def eco_impact(change):return sorted(CATEGORY_IMPACT.get(change.category,{"review"}))
