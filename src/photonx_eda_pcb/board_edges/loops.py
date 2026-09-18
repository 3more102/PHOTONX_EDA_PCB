from .model import EdgeLoop
from .snap import snap_point
def assemble_loops(segments,tol=1e-6):
    remaining=[(s.id,snap_point(s.start,tol),snap_point(s.end,tol)) for s in segments]
    loops=[]
    while remaining:
        sid,a,b=remaining.pop(0);pts=[a,b]
        while pts[-1]!=pts[0]:
            idx=next((i for i,(_,x,y) in enumerate(remaining) if x==pts[-1] or y==pts[-1]),None)
            if idx is None:break
            _,x,y=remaining.pop(idx);pts.append(y if x==pts[-1] else x)
        if len(pts)>=4 and pts[-1]==pts[0]:
            loops.append(EdgeLoop("loop:"+sid,tuple(pts[:-1]),False))
    return loops
