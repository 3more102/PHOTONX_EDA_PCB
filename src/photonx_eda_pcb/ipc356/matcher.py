from math import hypot
def nearest_pad(record,pads,tolerance_mm=0.15):
    if record.x is None or record.y is None:return None
    best=None
    for p in pads:
        c=getattr(p,"center",None)
        if c is None: continue
        d=hypot(float(c.x)-float(record.x),float(c.y)-float(record.y))
        if d<=tolerance_mm and (best is None or d<best[0]):best=(d,p)
    return None if best is None else best[1]
