def snap_value(value,grid=2.54):
    g=float(grid)
    if g<=0:raise ValueError("grid must be positive")
    return round(round(float(value)/g)*g,6)
def snap_point(point,grid=2.54):return (snap_value(point[0],grid),snap_value(point[1],grid))
