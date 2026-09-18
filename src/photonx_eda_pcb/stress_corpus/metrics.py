def board_size_metrics(board):
    return {"tracks":len(board.tracks),"pads":len(board.pads),"drills":len(board.drills),"objects":len(board.tracks)+len(board.pads)+len(board.drills)+len(board.outline)}
