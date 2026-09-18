def validate_pin_function(x):
    issues=[]
    if not 0<=x.confidence<=1:issues.append("PIN_FUNCTION_CONFIDENCE_RANGE")
    if not x.connector_id or not x.pin:issues.append("PIN_FUNCTION_ID_EMPTY")
    return issues
