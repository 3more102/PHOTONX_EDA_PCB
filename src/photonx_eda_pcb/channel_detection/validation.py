def validate_channel(c):
    issues=[]
    if len(c.instances)<2:issues.append("CHANNEL_TOO_FEW_INSTANCES")
    if not 0<=c.confidence<=1:issues.append("CHANNEL_CONFIDENCE_RANGE")
    return issues
