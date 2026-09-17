def board_object_counts(board):
    return {name:len(getattr(board,name,[]) or []) for name in ("tracks","pads","drills","components","nets")}
