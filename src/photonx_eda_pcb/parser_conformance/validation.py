def validate_conformance_case(c):
    issues=[]
    if not c.id.strip():issues.append("CONFORMANCE_ID_EMPTY")
    if c.format not in {"gerber","excellon"}:issues.append("CONFORMANCE_FORMAT_UNSUPPORTED")
    if not c.text.strip():issues.append("CONFORMANCE_TEXT_EMPTY")
    for k,v in c.expectation.counts.items():
        if int(v)<0:issues.append("CONFORMANCE_NEGATIVE_COUNT")
    return issues
