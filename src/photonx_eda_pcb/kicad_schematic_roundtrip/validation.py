def validate_roundtrip_read(data):
    issues=[];refs=[]
    if data.get("version") is None:issues.append("KICAD_RT_VERSION_MISSING")
    if data.get("generator") is None:issues.append("KICAD_RT_GENERATOR_MISSING")
    for s in data.get("symbols",[]):
        if not s.get("lib_id"):issues.append("KICAD_RT_SYMBOL_LIB_EMPTY")
        if s.get("reference"):refs.append(s["reference"])
    if len(refs)!=len(set(refs)):issues.append("KICAD_RT_DUPLICATE_REFERENCE")
    return issues
