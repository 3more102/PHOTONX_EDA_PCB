def validate_query(q):
    issues=[]
    if not q.field.strip():issues.append("QUERY_EMPTY_FIELD")
    if q.operator not in {"==","!=",">","<",">=","<=","~"}:issues.append("QUERY_BAD_OPERATOR")
    return issues
