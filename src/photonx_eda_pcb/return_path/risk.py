def return_path_risk(e):
    risk=(1-e.continuity_score)*.5+e.via_penalty*.25+min(1,e.split_crossings*.25)
    return round(min(1.0,max(0.0,risk)),6)
