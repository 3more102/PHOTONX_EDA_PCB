def validate_request(r):
    issues=[]
    if not r.path:issues.append("IMPORT_PATH_EMPTY")
    if r.text is None:issues.append("IMPORT_TEXT_NONE")
    return issues
