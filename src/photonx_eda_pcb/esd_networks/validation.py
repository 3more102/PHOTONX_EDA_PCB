def validate_esd_network(n):
    issues=[]
    if not n.protection_components:issues.append("ESD_NETWORK_NO_COMPONENT")
    if not 0<=n.confidence<=1:issues.append("ESD_NETWORK_CONFIDENCE_RANGE")
    return issues
