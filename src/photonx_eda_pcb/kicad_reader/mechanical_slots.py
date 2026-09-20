from math import cos,sin,radians,hypot
from photonx_eda_pcb.ids import stable_id
from photonx_eda_pcb.mechanical_features.model import SlotFeature

def _rotate(x,y,angle_deg):
    a=radians(angle_deg);return (x*cos(a)-y*sin(a),x*sin(a)+y*cos(a))

def _slot_from_pad(fp,index,pad):
    if pad.get("drill_shape")!="oval" or not pad.get("drill_size"):return None
    fx,fy=fp.get("at",(0.0,0.0));fa=float(fp.get("angle",0.0));px,py=pad.get("at",(0.0,0.0))
    ox,oy=pad.get("drill_offset",(0.0,0.0));pa=float(pad.get("angle",0.0))
    rx,ry=_rotate(px,py,fa);center=(fx+rx,fy+ry)
    dox,doy=_rotate(ox,oy,fa+pa);center=(center[0]+dox,center[1]+doy)
    a,b=map(float,pad["drill_size"]);major=max(a,b);minor=min(a,b)
    angle=fa+pa+(90.0 if b>a else 0.0);centerline=max(0.0,major-minor)
    vx,vy=_rotate(centerline/2,0,angle)
    start=(center[0]-vx,center[1]-vy);end=(center[0]+vx,center[1]+vy)
    kind=str(pad.get("kind",""));plating="non-plated" if kind=="np_thru_hole" else ("plated" if kind=="thru_hole" else "unknown")
    sid=stable_id("kicad-slot",fp.get("name",""),index,pad.get("number",""),round(center[0],6),round(center[1],6),round(major,6),round(minor,6))
    return SlotFeature(sid,start,end,minor,plating,None)

def read_mechanical_slots(footprints):
    out=[]
    route_footprints={
        "PHOTONX:RecoveredNPTHRoute",
        "PHOTONX:RecoveredPlatedRoute",
    }
    for fi,fp in enumerate(footprints):
        if fp.get("name") in route_footprints:
            continue
        for pi,pad in enumerate(fp.get("pads",())):
            slot=_slot_from_pad(fp,f"{fi}:{pi}",pad)
            if slot is not None:out.append(slot)
    return out
