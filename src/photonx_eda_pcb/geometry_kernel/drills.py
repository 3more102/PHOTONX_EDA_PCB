from shapely.geometry import Point as SPoint,LineString
def drill_shape(drill):
    start=getattr(drill,"start",None);end=getattr(drill,"end",None)
    diameter=float(getattr(drill,"diameter",0.0))
    if start is not None and end is not None:
        return LineString([(start.x,start.y),(end.x,end.y)]).buffer(diameter/2,cap_style=1)
    return SPoint(drill.center.x,drill.center.y).buffer(diameter/2)
