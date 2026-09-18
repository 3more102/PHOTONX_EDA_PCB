def courtyard_clearance(a_bounds,b_bounds):
    ax0,ay0,ax1,ay1=map(float,a_bounds);bx0,by0,bx1,by1=map(float,b_bounds)
    dx=max(bx0-ax1,ax0-bx1,0.0);dy=max(by0-ay1,ay0-by1,0.0)
    if dx==0 and dy==0:return 0.0
    return (dx*dx+dy*dy)**0.5
