from dataclasses import replace
def expand_keepout(k,margin_mm):
    m=float(margin_mm);x0,y0,x1,y1=k.bounds
    return replace(k,bounds=(x0-m,y0-m,x1+m,y1+m))
