def validate_panel(panel):
    issues=[]
    if not 0<=panel.confidence<=1:issues.append("PANEL_CONFIDENCE_RANGE")
    ids=[b.id for b in panel.boards]
    if len(ids)!=len(set(ids)):issues.append("PANEL_DUPLICATE_BOARD_ID")
    return issues
