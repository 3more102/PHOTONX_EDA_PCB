def expanded_size(size_x,size_y,expansion_mm=0.05):
    e=max(0.0,float(expansion_mm))
    return (float(size_x)+2*e,float(size_y)+2*e)
