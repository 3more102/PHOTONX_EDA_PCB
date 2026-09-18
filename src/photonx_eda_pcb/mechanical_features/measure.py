from math import hypot,atan2,degrees
def slot_geometry_descriptor(slot):
    x0,y0=map(float,slot.start);x1,y1=map(float,slot.end);w=float(slot.width_mm)
    dx=x1-x0;dy=y1-y0;center=((x0+x1)/2,(y0+y1)/2);centerline=hypot(dx,dy)
    return {"center":center,"centerline_mm":centerline,"long_mm":centerline+w,"short_mm":w,"angle_deg":degrees(atan2(dy,dx)) if centerline else 0.0}
