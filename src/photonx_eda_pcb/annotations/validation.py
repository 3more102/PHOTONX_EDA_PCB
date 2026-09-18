def validate_annotations(store):
    issues=[];ids=set()
    for x in store.items:
        if x.id in ids:issues.append("ANNOTATION_DUPLICATE_ID")
        ids.add(x.id)
        if not x.text.strip():issues.append("ANNOTATION_EMPTY_TEXT")
        if not x.object_id.strip():issues.append("ANNOTATION_EMPTY_OBJECT")
    return issues
