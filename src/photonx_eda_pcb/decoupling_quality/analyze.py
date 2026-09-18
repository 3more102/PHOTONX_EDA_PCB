from .model import DecouplingQuality
def analyze_decoupling(observations):
    out=[]
    for o in observations:
        score=.4;conf=.4;ev=["power_ground_connection"]
        if o.distance_mm is not None:
            d=max(0,float(o.distance_mm));score+=.35*max(0,1-min(d/10,1));conf+=.25;ev.append("distance")
        if o.capacitance_f is not None:
            c=max(0,float(o.capacitance_f));score+=.25*min(1,c/1e-6);conf+=.25;ev.append("capacitance")
        out.append(DecouplingQuality(o.component_id,o.power_net,round(min(score,1),6),round(min(conf,1),6),tuple(ev)))
    return sorted(out,key=lambda x:(x.power_net,-x.score,x.component_id))
