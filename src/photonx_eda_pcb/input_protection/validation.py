def validate_input_path(p):
    issues=[]
    if not p.protection_components:issues.append("INPUT_PROTECTION_EMPTY")
    if not 0<=p.confidence<=1:issues.append("INPUT_PROTECTION_CONFIDENCE_RANGE")
    return issues
