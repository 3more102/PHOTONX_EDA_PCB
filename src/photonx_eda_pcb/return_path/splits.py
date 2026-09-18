def split_crossing_risk(crossings,total_segments):
    if total_segments<=0:return 0.0
    return round(min(1.0,max(0,int(crossings))/int(total_segments)),6)
