from math import isfinite
from .base import RuleIssue
def positive_geometry(board):
    out=[]
    for t in getattr(board,'tracks',[]):
        if not isfinite(t.width) or t.width<=0: out.append(RuleIssue('error','TRACK_WIDTH','track width must be finite and positive',t.id))
    for p in getattr(board,'pads',[]):
        if p.size_x<=0 or p.size_y<=0: out.append(RuleIssue('error','PAD_SIZE','pad dimensions must be positive',p.id))
    for d in getattr(board,'drills',[]):
        if d.diameter<=0: out.append(RuleIssue('error','DRILL_DIAMETER','drill diameter must be positive',d.id))
    return out
