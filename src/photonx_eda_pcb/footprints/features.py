from collections import Counter
from math import atan2,cos,hypot,isfinite,sin
from statistics import median


def _coefficient_of_variation(values):
    values=[float(value) for value in values if isfinite(float(value))]
    if not values:
        return None
    mean=sum(values)/len(values)
    if mean<=0:
        return None
    variance=sum((value-mean)**2 for value in values)/len(values)
    return variance**0.5/mean


def _cluster_axis(values,tolerance):
    values=sorted(float(value) for value in values)
    if not values:
        return (),()
    groups=[[values[0]]]
    for value in values[1:]:
        center=sum(groups[-1])/len(groups[-1])
        if abs(value-center)<=tolerance:
            groups[-1].append(value)
        else:
            groups.append([value])
    centers=tuple(sum(group)/len(group) for group in groups)
    return tuple(len(group) for group in groups),centers


def _pitch_cv(centers):
    gaps=[b-a for a,b in zip(centers,centers[1:]) if b-a>0]
    return _coefficient_of_variation(gaps) if gaps else None


def _principal_layout(pads,cx,cy):
    if len(pads)<2:
        return {
            'principal_angle_deg':0.0,
            'primary_group_sizes':(len(pads),) if pads else (),
            'secondary_group_sizes':(len(pads),) if pads else (),
            'primary_pitch_cv':None,
            'secondary_pitch_cv':None,
        }
    xx=sum((p.center.x-cx)**2 for p in pads)
    yy=sum((p.center.y-cy)**2 for p in pads)
    xy=sum((p.center.x-cx)*(p.center.y-cy) for p in pads)
    angle=0.5*atan2(2*xy,xx-yy)
    ca,sa=cos(angle),sin(angle)
    primary=[]
    secondary=[]
    for pad in pads:
        dx=pad.center.x-cx
        dy=pad.center.y-cy
        primary.append(dx*ca+dy*sa)
        secondary.append(-dx*sa+dy*ca)
    short_sizes=[
        min(float(p.size_x),float(p.size_y))
        for p in pads
        if isfinite(float(p.size_x)) and isfinite(float(p.size_y))
        and float(p.size_x)>0 and float(p.size_y)>0
    ]
    tolerance=max(0.05,(median(short_sizes)*0.35 if short_sizes else 0.05))
    primary_sizes,primary_centers=_cluster_axis(primary,tolerance)
    secondary_sizes,secondary_centers=_cluster_axis(secondary,tolerance)
    return {
        'principal_angle_deg':angle*180.0/3.141592653589793,
        'primary_group_sizes':primary_sizes,
        'secondary_group_sizes':secondary_sizes,
        'primary_pitch_cv':_pitch_cv(primary_centers),
        'secondary_pitch_cv':_pitch_cv(secondary_centers),
    }


def extract_group_features(pads):
    pads=list(pads)
    if not pads:
        return {
            'count':0,
            'bbox':(0,0,0,0),
            'centroid':(0,0),
            'drilled_fraction':0.0,
            'pitch_min':None,
            'bbox_aspect':1.0,
            'pad_area_cv':None,
            'shape_uniformity':0.0,
            'layer_count':0,
            'principal_angle_deg':0.0,
            'primary_group_sizes':(),
            'secondary_group_sizes':(),
            'primary_pitch_cv':None,
            'secondary_pitch_cv':None,
        }
    xs=[p.center.x for p in pads]
    ys=[p.center.y for p in pads]
    n=len(pads)
    distances=[]
    for i,a in enumerate(pads):
        for b in pads[i+1:]:
            distances.append(hypot(a.center.x-b.center.x,a.center.y-b.center.y))
    x0,y0,x1,y1=min(xs),min(ys),max(xs),max(ys)
    width=max(x1-x0,1e-9)
    height=max(y1-y0,1e-9)
    areas=[
        float(p.size_x)*float(p.size_y)
        for p in pads
        if isfinite(float(p.size_x)) and isfinite(float(p.size_y))
        and float(p.size_x)>0 and float(p.size_y)>0
    ]
    shapes=Counter(str(p.shape) for p in pads)
    cx,cy=sum(xs)/n,sum(ys)/n
    layout=_principal_layout(pads,cx,cy)
    return {
        'count':n,
        'bbox':(x0,y0,x1,y1),
        'centroid':(cx,cy),
        'drilled_fraction':sum(p.drill is not None for p in pads)/n,
        'pitch_min':min(distances) if distances else None,
        'bbox_aspect':max(width/height,height/width),
        'pad_area_cv':_coefficient_of_variation(areas),
        'shape_uniformity':max(shapes.values())/n if shapes else 0.0,
        'layer_count':len({str(p.layer) for p in pads}),
        **layout,
    }
