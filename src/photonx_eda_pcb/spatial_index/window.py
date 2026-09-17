from .bbox import BBox
def around(x,y,radius): return BBox(x-radius,y-radius,x+radius,y+radius)
