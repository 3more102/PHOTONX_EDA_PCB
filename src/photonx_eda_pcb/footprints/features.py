from math import hypot

def extract_group_features(pads):
    if not pads:return {'count':0,'bbox':(0,0,0,0),'centroid':(0,0),'drilled_fraction':0.0,'pitch_min':None}
    xs=[p.center.x for p in pads]; ys=[p.center.y for p in pads]; n=len(pads)
    d=[]
    for i,a in enumerate(pads):
        for b in pads[i+1:]: d.append(hypot(a.center.x-b.center.x,a.center.y-b.center.y))
    return {'count':n,'bbox':(min(xs),min(ys),max(xs),max(ys)),'centroid':(sum(xs)/n,sum(ys)/n),'drilled_fraction':sum(p.drill is not None for p in pads)/n,'pitch_min':min(d) if d else None}
