def validate_controller_state(project=None,selection=None,viewport=None):
    issues=[]
    if viewport is not None and viewport.viewport.zoom<=0:issues.append("CONTROLLER_BAD_ZOOM")
    if selection is not None and selection.state.primary is not None and selection.state.primary not in selection.state.ids:issues.append("CONTROLLER_PRIMARY_NOT_SELECTED")
    return issues
