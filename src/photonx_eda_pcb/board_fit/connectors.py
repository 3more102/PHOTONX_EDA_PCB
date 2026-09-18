def connector_edge_distance(center,board_bounds):
    x,y=map(float,center);x0,y0,x1,y1=map(float,board_bounds)
    return min(abs(x-x0),abs(x-x1),abs(y-y0),abs(y-y1))
