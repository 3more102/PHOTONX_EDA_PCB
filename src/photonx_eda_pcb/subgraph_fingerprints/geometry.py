from math import hypot
def relative_geometry_signature(component_ids,centers):
    pts=[(c,centers[c]) for c in sorted(component_ids) if c in centers]
    if not pts:return ()
    ox=sum(float(p[0]) for _,p in pts)/len(pts);oy=sum(float(p[1]) for _,p in pts)/len(pts)
    return tuple((c,round(hypot(float(p[0])-ox,float(p[1])-oy),6)) for c,p in pts)
def geometry_similarity(a,b,tolerance_mm=.1):
    if len(a)!=len(b):return 0.0
    if not a and not b:return 1.0
    diffs=[abs(float(x[1])-float(y[1])) for x,y in zip(a,b)]
    return round(sum(d<=tolerance_mm for d in diffs)/len(diffs),6)
