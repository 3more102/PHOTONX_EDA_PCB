def thermal_confidence(spoke_count,gap_known=False,zone_match=False,symmetry=False):
    score=0.15
    if spoke_count>=2:score+=0.3
    if spoke_count>=4:score+=0.15
    if gap_known:score+=0.15
    if zone_match:score+=0.15
    if symmetry:score+=0.1
    return round(min(score,1.0),12)
