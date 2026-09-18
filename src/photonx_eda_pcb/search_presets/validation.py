from photonx_eda_pcb.query_engine import parse_query
def validate_preset(p):
    issues=[]
    if not p.name.strip():issues.append("PRESET_NAME_EMPTY")
    try:parse_query(p.query)
    except Exception:issues.append("PRESET_QUERY_INVALID")
    return issues
