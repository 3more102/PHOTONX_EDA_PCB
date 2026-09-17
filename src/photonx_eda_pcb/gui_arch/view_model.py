def board_view_model(board):
    return {'counts':{k:len(getattr(board,k)) for k in ('tracks','pads','drills','outline','nets','components')},'layers':sorted({o.layer for o in [*board.tracks,*board.pads] if getattr(o,'layer',None)})}
