def validate_session(s):
    issues=[]
    if not s.project_name.strip():issues.append("SESSION_EMPTY_PROJECT_NAME")
    if s.revision<0:issues.append("SESSION_NEGATIVE_REVISION")
    if len(s.open_documents)!=len(set(s.open_documents)):issues.append("SESSION_DUPLICATE_DOCUMENT")
    return issues
