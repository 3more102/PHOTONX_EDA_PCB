KNOWN_PREFIX={"D":"data","A":"address","DQ":"memory_data","ADDR":"address","DATA":"data","GPIO":"gpio","AD":"multiplexed_address_data"}
def bus_role(candidate):
    name=candidate.name.upper()
    for prefix,role in sorted(KNOWN_PREFIX.items(),key=lambda x:-len(x[0])):
        if name==prefix or name.startswith(prefix+"_"):return role
    return "unknown"
