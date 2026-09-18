def object_bbox(obj,symbol_half=(5.0,3.0)):
    name=obj.__class__.__name__
    if name=="EditorSymbol":
        hx,hy=symbol_half;return (obj.x-hx,obj.y-hy,obj.x+hx,obj.y+hy)
    if name=="EditorLabel":return (obj.x-1,obj.y-1,obj.x+1,obj.y+1)
    pts=getattr(obj,"points",())
    if pts:
        xs=[p[0] for p in pts];ys=[p[1] for p in pts];return (min(xs),min(ys),max(xs),max(ys))
    return (0,0,0,0)
def bbox_contains(box,x,y,tolerance=0):
    x0,y0,x1,y1=box;t=float(tolerance);return x0-t<=x<=x1+t and y0-t<=y<=y1+t
