def validate_serial_link(link):
    issues=[]
    if not 0<=link.confidence<=1:issues.append("SERIAL_CONFIDENCE_RANGE")
    if not link.protocol:issues.append("SERIAL_PROTOCOL_EMPTY")
    if len(set(link.nets))!=len(link.nets):issues.append("SERIAL_DUPLICATE_NET")
    return issues
