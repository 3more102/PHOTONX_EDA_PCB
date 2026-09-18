from math import hypot
def track_length(track):
    return hypot(float(track.end.x)-float(track.start.x),float(track.end.y)-float(track.start.y))
def net_lengths(tracks):
    out={}
    for t in tracks:
        if t.net_id is not None:out[t.net_id]=out.get(t.net_id,0.0)+track_length(t)
    return out
