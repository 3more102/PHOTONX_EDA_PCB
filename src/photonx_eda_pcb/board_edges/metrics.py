from math import hypot
def loop_perimeter(loop):
    p=loop.points
    return sum(hypot(p[(i+1)%len(p)][0]-p[i][0],p[(i+1)%len(p)][1]-p[i][1]) for i in range(len(p)))
def bounds(loop):
    xs=[p[0] for p in loop.points];ys=[p[1] for p in loop.points]
    return (min(xs),min(ys),max(xs),max(ys))
