def validate_connector_path(p):
    issues=[]
    if p.hops!=max(0,len(p.nodes)-1):issues.append("CONNECTOR_PATH_HOP_MISMATCH")
    if not 0<=p.confidence<=1:issues.append("CONNECTOR_PATH_CONFIDENCE_RANGE")
    return issues
