from math import hypot
from .apply import apply_transform
def rms_error(source_points,target_points,transform):
    if not source_points:return 0.0
    sq=[]
    for a,b in zip(source_points,target_points):
        x,y=apply_transform(a,transform);sq.append(hypot(x-b[0],y-b[1])**2)
    return (sum(sq)/len(sq))**0.5
