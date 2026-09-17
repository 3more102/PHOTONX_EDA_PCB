from math import atan2

def pin_order(pads):
    if not pads:return []
    cx=sum(p.center.x for p in pads)/len(pads); cy=sum(p.center.y for p in pads)/len(pads)
    return [p.id for p in sorted(pads,key=lambda p:(atan2(p.center.y-cy,p.center.x-cx),p.id))]
