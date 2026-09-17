from math import hypot

def pad_features(pads):
    if not pads:return {'count':0,'drilled':0,'span_x':0.0,'span_y':0.0,'pitch_min':None}
    xs=[p.center.x for p in pads]; ys=[p.center.y for p in pads]
    d=[hypot(a.center.x-b.center.x,a.center.y-b.center.y) for i,a in enumerate(pads) for b in pads[i+1:]]
    return {'count':len(pads),'drilled':sum(getattr(p,'drill',None) is not None for p in pads),'span_x':max(xs)-min(xs),'span_y':max(ys)-min(ys),'pitch_min':min(d) if d else None}
