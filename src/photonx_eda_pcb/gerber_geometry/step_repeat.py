def offsets(nx=1,ny=1,dx=0.0,dy=0.0):
    if nx<1 or ny<1: raise ValueError('repeat counts must be positive')
    return [(ix*dx,iy*dy) for iy in range(ny) for ix in range(nx)]
