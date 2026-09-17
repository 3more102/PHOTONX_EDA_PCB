from .statistics import zone_statistics

def zone_report(zones):
    s=zone_statistics(zones)
    return f"zones={s['zones']} islands={s['islands']} area_mm2={s['area_mm2']}"
