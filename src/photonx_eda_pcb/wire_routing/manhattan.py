def manhattan_points(start,end,prefer_horizontal=True):
    x0,y0=map(float,start);x1,y1=map(float,end)
    if x0==x1 or y0==y1:return ((x0,y0),(x1,y1))
    bend=(x1,y0) if prefer_horizontal else (x0,y1)
    return ((x0,y0),bend,(x1,y1))
