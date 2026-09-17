def near(a:float,b:float,tol:float=1e-6)->bool:
    if tol<0: raise ValueError("tol must be non-negative")
    return abs(a-b)<=tol
def point_near(a,b,tol:float=1e-6)->bool: return near(a.x,b.x,tol) and near(a.y,b.y,tol)
