def validate_observation(o):
    issues=[]
    if not o.source:issues.append('SOURCE_NAME_EMPTY')
    if not o.subject_id:issues.append('SOURCE_SUBJECT_EMPTY')
    if not o.field:issues.append('SOURCE_FIELD_EMPTY')
    if not 0<=o.confidence<=1:issues.append('SOURCE_CONFIDENCE_RANGE')
    return issues
