def validate_document(d):
    issues=[]
    if not d.path:issues.append("SOURCE_PATH_EMPTY")
    if not d.format:issues.append("SOURCE_FORMAT_EMPTY")
    return issues
