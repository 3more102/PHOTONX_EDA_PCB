from __future__ import annotations
from math import isfinite
from ..models import BoardModel

def board_bounds(board: BoardModel):
    boxes=[]
    def pt(x,y,r=0.0):
        v=(float(x)-r,float(y)-r,float(x)+r,float(y)+r)
        if all(isfinite(n) for n in v): boxes.append(v)
    for x in board.outline:
        pt(x.start.x,x.start.y); pt(x.end.x,x.end.y)
    for x in board.tracks:
        r=max(0.0,float(x.width))/2; pt(x.start.x,x.start.y,r); pt(x.end.x,x.end.y,r)
    for x in board.pads:
        rx=max(0.0,float(x.size_x))/2; ry=max(0.0,float(x.size_y))/2
        boxes.append((x.center.x-rx,x.center.y-ry,x.center.x+rx,x.center.y+ry))
    for x in board.drills: pt(x.center.x,x.center.y,max(0.0,float(x.diameter))/2)
    for x in board.slots:
        r=max(0.0,float(x.width_mm))/2; pt(*x.start,r); pt(*x.end,r)
    for x in board.routes:
        r=max(0.0,float(x.width_mm))/2
        for p in x.points: pt(*p,r)
    for x in board.regions:
        for p in x.points: pt(p.x,p.y)
    if not boxes:return None
    return (min(x[0] for x in boxes),min(x[1] for x in boxes),max(x[2] for x in boxes),max(x[3] for x in boxes))

def fit_view(bounds,width,height,padding=30.0):
    if bounds is None:return 12.0,30.0,30.0
    w=max(1.0,float(width)); h=max(1.0,float(height)); p=min(max(0.0,padding),min(w,h)/2)
    x0,y0,x1,y1=bounds; sx=max(0.0,x1-x0); sy=max(0.0,y1-y0)
    scale=min((w-2*p)/sx if sx else 500.0,(h-2*p)/sy if sy else 500.0,500.0)
    scale=max(0.05,scale); cx=(x0+x1)/2; cy=(y0+y1)/2
    return scale,w/2-cx*scale,h/2-cy*scale

def zoom_about(scale,ox,oy,sx,sy,factor):
    if scale<=0 or factor<=0:raise ValueError("scale and factor must be positive")
    ns=min(500.0,max(0.05,float(scale)*float(factor)))
    wx=(sx-ox)/scale; wy=(sy-oy)/scale
    return ns,sx-wx*ns,sy-wy*ns
