from math import hypot
from .model import BoardStats
def compute_board_stats(board):
    length=sum(hypot(float(t.end.x)-float(t.start.x),float(t.end.y)-float(t.start.y)) for t in board.tracks)
    pts=[]
    for s in board.outline:pts.extend([(float(s.start.x),float(s.start.y)),(float(s.end.x),float(s.end.y))])
    if pts:
        xs=[p[0] for p in pts];ys=[p[1] for p in pts];w=max(xs)-min(xs);h=max(ys)-min(ys)
    else:w=h=None
    return BoardStats(len(board.tracks),len(board.pads),len(board.drills),len(board.outline),len(board.nets),len(board.components),round(length,6),None if w is None else round(w,6),None if h is None else round(h,6))
