def validate_board_fit(x):
    issues=[]
    if not 0<=x.confidence<=1:issues.append("BOARD_FIT_CONFIDENCE_RANGE")
    if len(x.edge_margins)!=4:issues.append("BOARD_FIT_MARGIN_COUNT")
    return issues
