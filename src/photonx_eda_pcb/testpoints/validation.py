def validate_testpoint(tp):
    issues=[]
    if not tp.object_id:issues.append('TESTPOINT_OBJECT_MISSING')
    if tp.diameter_mm<=0:issues.append('TESTPOINT_DIAMETER_INVALID')
    if not 0<=tp.confidence<=1:issues.append('TESTPOINT_CONFIDENCE_RANGE')
    return issues
