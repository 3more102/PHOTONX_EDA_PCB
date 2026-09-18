def classify_change(change):
    if change.change_type!="modified":return change.change_type
    if change.before and change.after:
        if change.before.sha256!=change.after.sha256:return "content_modified"
        if change.before.role!=change.after.role:return "role_modified"
        if change.before.size!=change.after.size:return "size_modified"
    return "modified"
