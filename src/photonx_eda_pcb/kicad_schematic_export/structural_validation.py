from photonx_eda_pcb.kicad_reader.sexpr import parse_sexpr
def validate_text_structure(text):
    issues=[]
    try:root=parse_sexpr(text)
    except Exception as exc:return [f"KICAD_EXPORT_PARSE_ERROR:{type(exc).__name__}"]
    if not isinstance(root,list) or not root or root[0]!="kicad_sch":issues.append("KICAD_EXPORT_ROOT")
    tokens=[x[0] for x in root[1:] if isinstance(x,list) and x]
    for required in ("version","generator","uuid","lib_symbols"):
        if required not in tokens:issues.append("KICAD_EXPORT_MISSING_"+required.upper())
    return issues
