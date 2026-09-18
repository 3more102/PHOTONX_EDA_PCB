from shapely.geometry import Point as SPoint,box,LineString
from shapely.affinity import scale,rotate

def _oval(cx,cy,sx,sy):
    sx=float(sx);sy=float(sy)
    if sx<=0 or sy<=0:return SPoint(cx,cy).buffer(0)
    if abs(sx-sy)<1e-15:return SPoint(cx,cy).buffer(sx/2)
    if sx>sy:
        half=(sx-sy)/2
        return LineString([(cx-half,cy),(cx+half,cy)]).buffer(sy/2,cap_style=1)
    half=(sy-sx)/2
    return LineString([(cx,cy-half),(cx,cy+half)]).buffer(sx/2,cap_style=1)

def pad_shape(pad):
    cx=float(pad.center.x);cy=float(pad.center.y);sx=float(pad.size_x);sy=float(pad.size_y)
    shape=str(getattr(pad,"shape","C") or "C").upper()
    if shape=="C":
        if abs(sx-sy)<1e-15:geom=SPoint(cx,cy).buffer(sx/2)
        else:geom=scale(SPoint(cx,cy).buffer(.5),sx,sy,origin=(cx,cy))
    elif shape=="O":
        geom=_oval(cx,cy,sx,sy)
    else:
        geom=box(cx-sx/2,cy-sy/2,cx+sx/2,cy+sy/2)
    angle=float(getattr(pad,"rotation_deg",getattr(pad,"rotation",0.0)) or 0.0)
    return rotate(geom,angle,origin=(cx,cy),use_radians=False) if angle%360 else geom
