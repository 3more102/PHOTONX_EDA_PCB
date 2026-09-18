def validate_case(case):
    issues=[]
    if not case.id:issues.append("CORPUS_EMPTY_ID")
    if not case.input_paths:issues.append("CORPUS_NO_INPUTS")
    return issues
