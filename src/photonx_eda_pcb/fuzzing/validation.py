def validate_case(case):
    issues=[]
    if not case.name:issues.append('FUZZ_CASE_NAME_EMPTY')
    if not isinstance(case.payload,str):issues.append('FUZZ_PAYLOAD_NOT_TEXT')
    return issues
