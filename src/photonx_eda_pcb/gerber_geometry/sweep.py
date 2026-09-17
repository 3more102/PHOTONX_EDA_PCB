from .model import GeoPoint
def line_bbox(start:GeoPoint,end:GeoPoint,width:float):
    r=max(width,0)/2; return (min(start.x,end.x)-r,min(start.y,end.y)-r,max(start.x,end.x)+r,max(start.y,end.y)+r)
