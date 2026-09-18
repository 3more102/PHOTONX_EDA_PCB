from math import hypot
def distance(a,b):return hypot(float(b[0])-float(a[0]),float(b[1])-float(a[1]))
def orthogonal_distance(a,b):return abs(float(b[0])-float(a[0]))+abs(float(b[1])-float(a[1]))
