def validate_schematic(s):
    issues=[];refs=[x.reference for x in s.symbols]
    if len(refs)!=len(set(refs)):issues.append("KICAD_SCH_DUPLICATE_REFERENCE")
    for x in s.symbols:
        if not x.library_id:issues.append("KICAD_SCH_EMPTY_LIBRARY_ID")
    return issues
