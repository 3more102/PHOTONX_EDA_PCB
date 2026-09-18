from .model import ThermalRisk
def analyze_thermal_risk(obs):
    score=0.0;confidence=0.0;ev=[];ass=[]
    if obs.power_w is not None:
        p=max(0,float(obs.power_w));score+=min(.55,p/5*.55);confidence+=.35;ev.append("power_estimate")
    else:ass.append("power_unknown")
    if obs.copper_area_mm2 is not None:
        a=max(0,float(obs.copper_area_mm2));score+=.25*(1-min(a/100,1));confidence+=.25;ev.append("copper_area")
    else:ass.append("copper_area_unknown")
    vias=max(0,int(obs.thermal_vias));score+=.15*(1-min(vias/6,1));confidence+=.15;ev.append("thermal_vias")
    if obs.ambient_c is not None:
        score+=min(.05,max(0,(float(obs.ambient_c)-25)/100));confidence+=.1;ev.append("ambient")
    else:ass.append("ambient_unknown")
    return ThermalRisk(obs.object_id,round(min(score,1),6),round(min(confidence,1),6),tuple(ev),tuple(ass))
