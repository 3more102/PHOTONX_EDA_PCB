from ..models import BoardModel
from .segment import segment_length
def total_track_length(board:BoardModel)->float: return sum(segment_length(t.start,t.end) for t in board.tracks)
def total_outline_length(board:BoardModel)->float: return sum(segment_length(s.start,s.end) for s in board.outline)
