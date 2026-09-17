def aperture_bbox(shape:str,x:float,y:float|None=None):
    s=shape.upper(); yy=x if y is None else y
    if x<=0 or yy<=0: raise ValueError('aperture dimensions must be positive')
    if s not in {'C','R','O','P'}: raise ValueError('unsupported aperture shape')
    return (-x/2,-yy/2,x/2,yy/2)
