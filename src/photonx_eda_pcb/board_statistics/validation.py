def validate_stats(s):
    issues=[]
    for name in ("tracks","pads","drills","outline_segments","nets","components"):
        if getattr(s,name)<0:issues.append("STATS_NEGATIVE_"+name.upper())
    if s.total_track_length_mm<0:issues.append("STATS_NEGATIVE_TRACK_LENGTH")
    return issues
