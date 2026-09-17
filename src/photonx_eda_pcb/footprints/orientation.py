from math import atan2,degrees

def principal_orientation_deg(pads):
    if len(pads)<2:return 0.0
    xs=[p.center.x for p in pads]; ys=[p.center.y for p in pads]; cx=sum(xs)/len(xs); cy=sum(ys)/len(ys)
    xx=sum((x-cx)**2 for x in xs); yy=sum((y-cy)**2 for y in ys); xy=sum((x-cx)*(y-cy) for x,y in zip(xs,ys))
    return 0.5*degrees(atan2(2*xy,xx-yy))
