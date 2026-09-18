from .model import YieldRisk
def estimate_yield_risk(m,rules=None):
    rules=rules or {"track":.15,"clearance":.15,"drill":.2};score=0;drivers=[]
    if m.min_track_mm is not None and m.min_track_mm<rules["track"]:score+=.25;drivers.append("track_below_rule")
    if m.min_clearance_mm is not None and m.min_clearance_mm<rules["clearance"]:score+=.3;drivers.append("clearance_below_rule")
    if m.min_drill_mm is not None and m.min_drill_mm<rules["drill"]:score+=.2;drivers.append("drill_below_rule")
    if m.acute_features>0:score+=min(.15,m.acute_features*.02);drivers.append("acute_features")
    density=0 if not m.board_area_mm2 else (m.track_count+m.via_count)/max(float(m.board_area_mm2),1e-9)
    if density>.5:score+=.1;drivers.append("high_feature_density")
    score=round(min(score,1),6);level="high" if score>=.65 else "medium" if score>=.35 else "low"
    return YieldRisk(score,level,tuple(drivers))
