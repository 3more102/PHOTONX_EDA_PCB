from math import hypot
def match_mounting_holes(board_holes,enclosure_holes,tolerance_mm=.25):
    used=set();matches=[]
    for i,a in enumerate(board_holes):
        best=None
        for j,b in enumerate(enclosure_holes):
            if j in used:continue
            d=hypot(float(a[0])-float(b[0]),float(a[1])-float(b[1]))
            if d<=tolerance_mm and (best is None or d<best[0]):best=(d,j)
        if best is not None:used.add(best[1]);matches.append((i,best[1],round(best[0],6)))
    return matches
