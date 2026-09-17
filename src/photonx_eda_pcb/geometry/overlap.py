def interval_overlap(a0:float,a1:float,b0:float,b1:float)->float:
    lo=max(min(a0,a1),min(b0,b1)); hi=min(max(a0,a1),max(b0,b1)); return max(0.0,hi-lo)
def intervals_touch(a0:float,a1:float,b0:float,b1:float,tol:float=0.0)->bool: return interval_overlap(a0,a1,b0,b1)>0 or abs(max(min(a0,a1),min(b0,b1))-min(max(a0,a1),max(b0,b1)))<=tol
