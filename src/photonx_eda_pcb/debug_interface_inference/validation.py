def validate_debug_interface(x):
    issues=[]
    if x.protocol not in {"SWD","JTAG"}:issues.append("DEBUG_PROTOCOL_UNKNOWN")
    if not 0<=x.confidence<=1:issues.append("DEBUG_CONFIDENCE_RANGE")
    return issues
