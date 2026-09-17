def polygon_area(points):
    if len(points)<3:return 0.0
    return abs(sum(x1*y2-x2*y1 for (x1,y1),(x2,y2) in zip(points,points[1:]+points[:1])))/2

def zone_area(zone):return sum(polygon_area(list(i.polygon)) for i in zone.islands)

def zone_bounds(zone):
    pts=[p for i in zone.islands for p in i.polygon]
    if not pts:return None
    xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
    return (min(xs),min(ys),max(xs),max(ys))
