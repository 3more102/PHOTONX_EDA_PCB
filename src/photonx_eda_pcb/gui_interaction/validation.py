def validate_viewport(v):
    return [] if v.zoom>0 else ["VIEWPORT_NONPOSITIVE_ZOOM"]
