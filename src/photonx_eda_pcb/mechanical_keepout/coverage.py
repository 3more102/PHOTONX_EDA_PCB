def keepout_area(k):
    x0,y0,x1,y1=map(float,k.bounds);return max(0,x1-x0)*max(0,y1-y0)
