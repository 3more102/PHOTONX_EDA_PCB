def board_size_issues(width_mm,height_mm,rules):
    out=[]
    if rules.max_board_width_mm is not None and width_mm>rules.max_board_width_mm:out.append('FAB_BOARD_WIDTH_EXCEEDED')
    if rules.max_board_height_mm is not None and height_mm>rules.max_board_height_mm:out.append('FAB_BOARD_HEIGHT_EXCEEDED')
    return out
