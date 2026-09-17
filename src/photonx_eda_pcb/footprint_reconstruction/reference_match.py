def match_reference(silk_tokens,center,max_distance_mm=5.0):
    best=None
    for t in silk_tokens:
        d=((t.x-center[0])**2+(t.y-center[1])**2)**0.5
        if d<=max_distance_mm and (best is None or d<best[0]):best=(d,t.text)
    return None if best is None else best[1]
