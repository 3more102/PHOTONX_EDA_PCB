def validate_checkpoint(c):
    issues=[]
    if not c.id.strip():issues.append("CHECKPOINT_ID_EMPTY")
    if not c.title.strip():issues.append("CHECKPOINT_TITLE_EMPTY")
    if len(c.required_items)!=len(set(c.required_items)):issues.append("CHECKPOINT_DUPLICATE_REQUIRED_ITEM")
    return issues
