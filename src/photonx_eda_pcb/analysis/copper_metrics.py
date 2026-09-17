from ..models import BoardModel
def copper_track_length_by_layer(board:BoardModel)->dict[str,float]:
    out={}
    from ..geometry.segment import segment_length
    for t in board.tracks:
        out[t.layer]=out.get(t.layer,0.0)+segment_length(t.start,t.end)
    return out
def average_track_width(board:BoardModel)->float: return 0.0 if not board.tracks else sum(t.width for t in board.tracks)/len(board.tracks)
