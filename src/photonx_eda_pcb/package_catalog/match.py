def match_package(catalog,*,pin_count,pitch_mm=None,mounting=None,pitch_tol=.15):
    out=[]
    for e in catalog.all():
        if e.pin_count!=int(pin_count):continue
        score=.6;reasons=["pin_count"]
        if mounting and e.mounting==mounting:score+=.2;reasons.append("mounting")
        if pitch_mm is not None and e.pitch_mm is not None and abs(float(pitch_mm)-e.pitch_mm)<=pitch_tol:score+=.2;reasons.append("pitch")
        out.append((round(min(score,1),12),e,reasons))
    return sorted(out,key=lambda x:(-x[0],x[1].name))
