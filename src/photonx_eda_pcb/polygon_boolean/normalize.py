def signed_area(points):
    pts=list(points)
    return 0.5*sum(pts[i][0]*pts[(i+1)%len(pts)][1]-pts[(i+1)%len(pts)][0]*pts[i][1] for i in range(len(pts)))
def normalize_polygon(points):
    pts=[(round(float(x),12),round(float(y),12)) for x,y in points]
    if len(pts)>1 and pts[0]==pts[-1]:pts.pop()
    if len(pts)<3:raise ValueError("polygon requires at least three unique points")
    if signed_area(pts)<0:pts.reverse()
    start=min(range(len(pts)),key=lambda i:pts[i])
    pts=pts[start:]+pts[:start]
    return tuple(pts)
