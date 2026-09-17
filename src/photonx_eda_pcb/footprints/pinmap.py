def radial_pin_order(pads):
    import math
    if not pads:return []
    cx=sum(p.center.x for p in pads)/len(pads); cy=sum(p.center.y for p in pads)/len(pads)
    return [p.id for p in sorted(pads,key=lambda p:(math.atan2(p.center.y-cy,p.center.x-cx),p.id))]
