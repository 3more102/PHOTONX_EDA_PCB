def reconstruction_confidence(has_cluster,package_hint=False,reference=False,external_match=False):
    score=0.2 if has_cluster else 0.0
    if package_hint:score+=0.25
    if reference:score+=0.2
    if external_match:score+=0.3
    return round(min(score,1.0),12)
