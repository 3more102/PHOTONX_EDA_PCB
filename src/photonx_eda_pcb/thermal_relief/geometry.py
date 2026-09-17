from math import cos,sin,radians

def spoke_endpoint(center,angle_deg,length_mm):
    a=radians(angle_deg)
    return (center[0]+cos(a)*length_mm,center[1]+sin(a)*length_mm)

def angular_gaps(spokes):
    a=sorted((s.angle_deg%360 for s in spokes))
    if len(a)<2:return []
    return [((a[(i+1)%len(a)]-a[i])%360) for i in range(len(a))]
