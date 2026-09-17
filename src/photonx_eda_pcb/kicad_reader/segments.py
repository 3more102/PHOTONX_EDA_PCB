from .query import children,child
def _xy(n): return (float(n[1]),float(n[2])) if n and len(n)>=3 else None
def read_segments(root):
    out=[]
    for s in children(root,'segment'):
        out.append({'start':_xy(child(s,'start')),'end':_xy(child(s,'end')),'width':float(child(s,'width')[1]),'layer':str(child(s,'layer')[1]),'net':int(child(s,'net')[1]) if child(s,'net') else None})
    return out
