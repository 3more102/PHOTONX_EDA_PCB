def validate_event(e):
    issues=[]
    if e.seq<=0:issues.append("EVENT_BAD_SEQUENCE")
    if not e.kind.strip():issues.append("EVENT_EMPTY_KIND")
    if not e.message.strip():issues.append("EVENT_EMPTY_MESSAGE")
    return issues
