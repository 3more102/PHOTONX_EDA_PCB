def violations_for_track(track,profile):
    rules={"min_track_mm":profile.min_track_mm}
    o=profile.net_overrides.get(str(getattr(track,"net_id",None)),{})
    rules.update(o)
    return ["TRACK_WIDTH"] if float(track.width)<float(rules["min_track_mm"]) else []
