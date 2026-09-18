from dataclasses import replace
def mirror_bottom_x(records,axis_x=0.0):
    out=[]
    for r in records:
        if r.side in {"bottom","back","b"}:out.append(replace(r,x_mm=2*float(axis_x)-r.x_mm,rotation_deg=(-r.rotation_deg)%360))
        else:out.append(r)
    return out
