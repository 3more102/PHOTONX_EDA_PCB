def validate_workspace(state):
    issues=[]
    if not state.project_name.strip(): issues.append(("error","WORKSPACE_NAME_EMPTY"))
    if not state.source_root.strip(): issues.append(("error","WORKSPACE_SOURCE_EMPTY"))
    return issues
