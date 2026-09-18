from .model import PasteAperture
from .reduction import reduced_size
def reconstruct_paste(pads,reduction_ratio=0.05,layer="F.Paste"):
    out=[]
    for p in pads:
        if isinstance(p,dict):
            pid=str(p["id"]);x,y=map(float,p["center"]);sx=float(p["size_x"]);sy=float(p["size_y"]);drill=p.get("drill")
        else:
            pid=str(p.id);x,y=float(p.center.x),float(p.center.y);sx=float(p.size_x);sy=float(p.size_y);drill=p.drill
        if drill not in (None,0):continue
        out.append(PasteAperture("paste:"+pid,(x,y),reduced_size(sx,sy,reduction_ratio),layer,pid))
    return out
