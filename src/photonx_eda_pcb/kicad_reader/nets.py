from .query import children
def read_nets(root):
    out=[]
    for n in children(root,'net'):
        if len(n)>=3: out.append({'code':int(n[1]),'name':str(n[2])})
    return out
