def validate_polarity(p):
    issues=[]
    if p.positive_pin is not None and p.positive_pin==p.negative_pin:issues.append("POLARITY_SAME_PIN")
    if not 0<=p.confidence<=1:issues.append("POLARITY_CONFIDENCE_RANGE")
    return issues
def validate_orientation(o):
    issues=[]
    if not 0<=o.rotation_deg<360:issues.append("ORIENTATION_ANGLE_RANGE")
    if not 0<=o.confidence<=1:issues.append("ORIENTATION_CONFIDENCE_RANGE")
    return issues
