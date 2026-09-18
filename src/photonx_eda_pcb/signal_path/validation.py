def validate_signal_path(path):
    issues=[]
    if path.hops!=max(0,len(path.nodes)-1):issues.append("SIGNAL_PATH_HOP_MISMATCH")
    if not 0<=path.confidence<=1:issues.append("SIGNAL_PATH_CONFIDENCE_RANGE")
    return issues
