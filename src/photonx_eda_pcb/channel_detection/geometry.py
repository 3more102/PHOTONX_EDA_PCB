def channel_spacing(instance_centers):
    pts=[p for p in instance_centers if p is not None]
    if len(pts)<2:return ()
    xs=sorted(float(p[0]) for p in pts);ys=sorted(float(p[1]) for p in pts)
    dx=tuple(round(b-a,6) for a,b in zip(xs,xs[1:]));dy=tuple(round(b-a,6) for a,b in zip(ys,ys[1:]))
    return dx,dy
def regular_spacing(spacing,tolerance=.1):
    values=[x for seq in spacing for x in seq if x>0]
    if len(values)<2:return False
    avg=sum(values)/len(values)
    return all(abs(x-avg)<=float(tolerance) for x in values)
