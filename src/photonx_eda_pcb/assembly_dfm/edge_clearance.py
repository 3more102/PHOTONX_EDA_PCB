def component_edge_clearance(center,board_bounds):
    x,y=map(float,center);x0,y0,x1,y1=map(float,board_bounds)
    return min(x-x0,x1-x,y-y0,y1-y)
