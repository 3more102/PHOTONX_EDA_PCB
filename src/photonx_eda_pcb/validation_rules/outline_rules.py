from math import hypot
from .base import RuleIssue
def outline_closed(board,tolerance:float=0.05):
    s=getattr(board,'outline',[])
    if not s: return [RuleIssue('warning','OUTLINE_MISSING','board outline is missing')]
    out=[]
    def dist(a,b): return hypot(a.x-b.x,a.y-b.y)
    for a,b in zip(s,s[1:]):
        if dist(a.end,b.start)>tolerance: out.append(RuleIssue('warning','OUTLINE_GAP','adjacent outline segments do not meet',a.id))
    if dist(s[-1].end,s[0].start)>tolerance: out.append(RuleIssue('warning','OUTLINE_OPEN','outline is not closed',s[-1].id))
    return out
