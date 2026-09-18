from math import cos,sin,radians
def apply_transform(point,t):
    x=float(point[0])*t.scale;y=float(point[1])*t.scale;a=radians(t.rotation_deg)
    return (x*cos(a)-y*sin(a)+t.dx,x*sin(a)+y*cos(a)+t.dy)
