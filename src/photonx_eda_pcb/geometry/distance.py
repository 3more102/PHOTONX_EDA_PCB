from math import hypot
from ..models import Point
def distance(a:Point,b:Point)->float: return hypot(a.x-b.x,a.y-b.y)
