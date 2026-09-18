from dataclasses import replace
def shift_origin(records,dx_mm=0.0,dy_mm=0.0):
    return [replace(r,x_mm=r.x_mm-float(dx_mm),y_mm=r.y_mm-float(dy_mm)) for r in records]
