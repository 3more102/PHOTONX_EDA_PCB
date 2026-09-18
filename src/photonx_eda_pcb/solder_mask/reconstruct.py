from .model import MaskOpening,MaskResult
from .expansion import expanded_size
def reconstruct_mask_openings(pads,layer="F.Mask",expansion_mm=0.05):
    out=[]
    for p in pads:
        pid=str(getattr(p,"id",p.get("id")))
        c=getattr(p,"center",None)
        if c is not None:
            x,y=float(c.x),float(c.y)
            sx,sy=float(getattr(p,"size_x")),float(getattr(p,"size_y"))
        else:
            x,y=map(float,p["center"]);sx=float(p["size_x"]);sy=float(p["size_y"])
        out.append(MaskOpening("mask:"+pid,(x,y),expanded_size(sx,sy,expansion_mm),layer,pid))
    return MaskResult(out,0.85 if out else 0.0,["derived_from_pad_geometry"] if out else [])
