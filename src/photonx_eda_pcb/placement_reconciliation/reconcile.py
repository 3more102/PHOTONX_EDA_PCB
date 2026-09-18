from .model import PlacementDelta
from .distance import placement_distance
from .angles import angle_delta
def reconcile_placements(source,reconstructed,pos_tol_mm=.25,rot_tol_deg=5):
    a={str(x.reference):x for x in source};b={str(x.reference):x for x in reconstructed};out=[]
    for ref in sorted(set(a)|set(b)):
        if ref not in a:out.append(PlacementDelta(ref,0,0,True,"ONLY_RECONSTRUCTED"));continue
        if ref not in b:out.append(PlacementDelta(ref,0,0,True,"ONLY_SOURCE"));continue
        x,y=a[ref],b[ref];d=placement_distance(x,y);r=angle_delta(x.rotation,y.rotation);side=str(x.side).lower()==str(y.side).lower()
        code="OK" if d<=pos_tol_mm and r<=rot_tol_deg and side else "PLACEMENT_MISMATCH"
        out.append(PlacementDelta(ref,round(d,6),round(r,6),side,code))
    return out
