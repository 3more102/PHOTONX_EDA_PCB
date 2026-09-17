def testpoint_score(tp):
    score=float(tp.confidence)
    if tp.net_id is not None:score+=0.15
    if tp.diameter_mm>=1.0:score+=0.1
    if tp.exposed:score+=0.05
    return round(min(score,1.0),12)

def rank_testpoints(items):return sorted(items,key=lambda x:(-testpoint_score(x),x.object_id))
