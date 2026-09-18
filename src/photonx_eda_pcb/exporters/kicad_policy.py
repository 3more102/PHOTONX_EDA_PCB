from math import hypot,atan2,degrees
def pad_shape_name(shape):
    s=str(shape or "").upper()
    if s=="C":return "circle"
    if s=="O":return "oval"
    if s=="R":return "rect"
    return "rect"

def slot_geometry(slot):
    x0,y0=map(float,slot.start);x1,y1=map(float,slot.end);w=float(slot.width_mm)
    dx=x1-x0;dy=y1-y0;center=((x0+x1)/2,(y0+y1)/2)
    centerline=hypot(dx,dy);long_dim=centerline+w;short_dim=w
    angle=degrees(atan2(dy,dx)) if centerline else 0.0
    return {"center":center,"long_mm":long_dim,"short_mm":short_dim,"angle_deg":angle}

def slot_export_status(slot):
    plating=str(getattr(slot,"plated","unknown")).lower().replace("_","-")
    if plating=="non-plated":return "export-npth"
    if plating=="plated":return "skip-plated-no-copper-stack"
    return "skip-unknown-plating"
