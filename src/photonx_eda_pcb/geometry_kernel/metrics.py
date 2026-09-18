def shape_metrics(shape):
    return {"area":float(shape.area),"length":float(shape.length),"bounds":tuple(float(x) for x in shape.bounds),"valid":bool(shape.is_valid),"empty":bool(shape.is_empty)}
