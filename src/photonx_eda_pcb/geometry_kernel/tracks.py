from shapely.geometry import LineString
def track_shape(track):
    return LineString([(track.start.x,track.start.y),(track.end.x,track.end.y)]).buffer(float(track.width)/2,cap_style=1)
