from .analysis import zone_area

def zone_statistics(zones):
    return {'zones':len(zones),'islands':sum(len(z.islands) for z in zones),'area_mm2':round(sum(zone_area(z) for z in zones),6)}
