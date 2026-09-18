def reduced_size(size_x,size_y,reduction_ratio=0.05):
    r=min(max(float(reduction_ratio),0.0),0.95)
    return (float(size_x)*(1-r),float(size_y)*(1-r))
