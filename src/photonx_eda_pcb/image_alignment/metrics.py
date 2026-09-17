from math import hypot,sqrt
def residuals(transform,points):
    result=[]
    for point in points:
        x,y=transform.apply(point.image_x,point.image_y); result.append(hypot(x-point.board_x,y-point.board_y))
    return tuple(result)
def rms_error(transform,points):
    values=residuals(transform,points)
    return 0.0 if not values else sqrt(sum(value*value for value in values)/len(values))
