def shape_bounds(shape):
    x0,y0,x1,y1=shape.bounds
    return (float(x0),float(y0),float(x1),float(y1))
def object_bounds(obj):
    from .objects import object_shape
    return shape_bounds(object_shape(obj))
