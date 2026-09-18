def snap_point(p,tol=1e-6):
    t=max(float(tol),1e-15)
    return (round(float(p[0])/t)*t,round(float(p[1])/t)*t)
