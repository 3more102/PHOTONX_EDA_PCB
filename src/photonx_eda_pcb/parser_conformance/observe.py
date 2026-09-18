def observe_parse_result(result):
    counts={}
    for field in ("tracks","pads","drills","slots","routes","outline"):
        if hasattr(result,field):counts[field]=len(getattr(result,field))
    diagnostics=tuple(sorted(getattr(x,"code","UNKNOWN") for x in getattr(result,"diagnostics",[])))
    return counts,diagnostics
