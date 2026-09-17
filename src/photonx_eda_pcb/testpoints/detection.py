from .model import TestPointCandidate

def detect_testpoints(objects,min_diameter_mm=0.6):
    out=[]
    for o in objects:
        d=float(getattr(o,'diameter_mm',getattr(o,'diameter',0.0)) or 0.0)
        exposed=bool(getattr(o,'exposed',False))
        if exposed and d>=min_diameter_mm:
            out.append(TestPointCandidate(str(getattr(o,'id','')),getattr(o,'net_id',None),d,True,0.7,['exposed copper','sufficient diameter']))
    return out
