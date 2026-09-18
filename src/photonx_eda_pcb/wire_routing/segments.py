def segments(route):return tuple((route.points[i],route.points[i+1]) for i in range(len(route.points)-1))
def route_length(route):
    return sum(abs(b[0]-a[0])+abs(b[1]-a[1]) for a,b in segments(route))
