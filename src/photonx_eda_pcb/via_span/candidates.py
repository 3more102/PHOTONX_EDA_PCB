from math import hypot

def pads_near_drill(board,drill,tolerance_mm=0.15):
    out=[]
    for p in board.pads:
        r=max(p.size_x,p.size_y)/2
        if hypot(p.center.x-drill.center.x,p.center.y-drill.center.y)<=max(tolerance_mm,r):out.append(p)
    return out
