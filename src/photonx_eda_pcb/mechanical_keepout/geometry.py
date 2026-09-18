def point_in_bounds(point,bounds):
    x,y=map(float,point);x0,y0,x1,y1=map(float,bounds)
    return x0<=x<=x1 and y0<=y<=y1
def bounds_overlap(a,b):
    ax0,ay0,ax1,ay1=map(float,a);bx0,by0,bx1,by1=map(float,b)
    return not (ax1<bx0 or bx1<ax0 or ay1<by0 or by1<ay0)
